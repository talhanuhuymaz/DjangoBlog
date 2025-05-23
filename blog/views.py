from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, UserProfile
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy

# Create your views here.
def test(request):
    return render(request,'blog/base.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('upassword')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Ensure the user has a profile
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                UserProfile.objects.create(user=user)
                
            login(request, user)
            return redirect('home-page')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'blog/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        email = request.POST.get('uemail')
        password = request.POST.get('upassword')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'blog/signup.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'blog/signup.html')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login-page')
        
    return render(request, 'blog/signup.html')

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked_posts'] = Post.objects.filter(likes=self.request.user).values_list('id', flat=True)
        return context

@login_required
def home(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        posts = Post.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        ).order_by('-date_posted')
    else:
        posts = Post.objects.all().order_by('-date_posted')
    
    context = {
        'posts': posts,
        'search_query': search_query
    }
    return render(request, 'blog/home.html', context)

@login_required
def new_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if title and content:
            try:
                post = Post.objects.create(
                    title=title,
                    content=content,
                    author=request.user
                )
                
                if image:
                    # Validate file size (max 5MB)
                    if image.size > 5 * 1024 * 1024:
                        post.delete()
                        messages.error(request, 'Image size should not exceed 5MB')
                        return redirect('home-page')
                    
                    # Validate file type
                    if not image.content_type.startswith('image/'):
                        post.delete()
                        messages.error(request, 'File must be an image')
                        return redirect('home-page')
                    
                    post.image = image
                    post.save()
                
                messages.success(request, 'Post created successfully!')
                return redirect('home-page')
            except Exception as e:
                messages.error(request, f'Error creating post: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields')
    
    return redirect('home-page')

@login_required
def my_posts(request):
    context = {
        'posts': Post.objects.filter(author=request.user).order_by('-date_posted')
    }
    return render(request, 'blog/my_posts.html', context)

@login_required
def signout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully!')
    return redirect('login-page')

@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user == post.author:
            # Check if post has image attribute and if it contains a file
            if hasattr(post, 'image') and bool(post.image):
                post.image.delete()  # Delete the image file
            post.delete()
            messages.success(request, 'Post deleted successfully!')
        else:
            messages.error(request, 'You can only delete your own posts!')
    return redirect('home-page')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        messages.error(request, 'You can only edit your own posts!')
        return redirect('home-page')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        delete_image = request.POST.get('delete_image') == 'true'
        
        if title and content:
            try:
                post.title = title
                post.content = content
                
                # Handle image
                if delete_image and post.image:
                    post.image.delete()
                    post.image = None
                elif image:
                    # Validate file size (max 5MB)
                    if image.size > 5 * 1024 * 1024:
                        messages.error(request, 'Image size should not exceed 5MB')
                        return redirect('home-page')
                    
                    # Validate file type
                    if not image.content_type.startswith('image/'):
                        messages.error(request, 'File must be an image')
                        return redirect('home-page')
                    
                    # Delete old image if exists
                    if post.image:
                        post.image.delete()
                    post.image = image
                
                post.save()
                messages.success(request, 'Post updated successfully!')
                return redirect('home-page')
            except Exception as e:
                messages.error(request, f'Error updating post: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields')
    
    return redirect('home-page')

def test_image(request, image_name):
    image_path = os.path.join(settings.MEDIA_ROOT, 'post_images', image_name)
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            return HttpResponse(img.read(), content_type='image/jpeg')
    return HttpResponse('Image not found', status=404)

@login_required
def profile(request):
    # Ensure user has a profile
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    # Define default avatars
    default_avatars = [
        {'name': 'Default 1', 'icon': 'fas fa-user-circle', 'color': '#4F46E5'},
        {'name': 'Default 2', 'icon': 'fas fa-user-ninja', 'color': '#7C3AED'},
        {'name': 'Default 3', 'icon': 'fas fa-user-astronaut', 'color': '#EC4899'},
        {'name': 'Default 4', 'icon': 'fas fa-user-tie', 'color': '#10B981'},
        {'name': 'Default 5', 'icon': 'fas fa-user-graduate', 'color': '#F59E0B'},
        {'name': 'Default 6', 'icon': 'fas fa-user-secret', 'color': '#6366F1'}
    ]

    if request.method == 'POST':
        # Get form data
        user = request.user
        username = request.POST.get('username')
        email = request.POST.get('email')
        avatar = request.FILES.get('avatar')
        selected_avatar = request.POST.get('selected_avatar')
        password = request.POST.get('password')
        
        # Verify password
        if not password or not user.check_password(password):
            messages.error(request, 'Current password is incorrect')
            return redirect('profile')
        
        # Check if username exists (excluding current user)
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'Username already exists')
            return redirect('profile')
        
        # Check if email exists (excluding current user)
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already exists')
            return redirect('profile')
        
        try:
            # Update user information
            user.username = username
            user.email = email
            user.save()
            
            # Handle avatar update
            if avatar:
                # Validate file size (max 2MB)
                if avatar.size > 2 * 1024 * 1024:
                    messages.error(request, 'Avatar size should not exceed 2MB')
                    return redirect('profile')
                
                # Validate file type
                if not avatar.content_type.startswith('image/'):
                    messages.error(request, 'File must be an image')
                    return redirect('profile')
                
                # Delete old avatar if it's not the default
                if user.profile.avatar and not user.profile.avatar.name.startswith('default_avatar_'):
                    user.profile.avatar.delete()
                user.profile.avatar = avatar
                user.profile.save()
            elif selected_avatar:
                # Update selected default avatar
                user.profile.selected_avatar = selected_avatar
                user.profile.selected_avatar_color = next((a['color'] for a in default_avatars if a['icon'] == selected_avatar), '#4F46E5')
                user.profile.avatar = None
                user.profile.save()
            
            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
        
        return redirect('profile')
    
    context = {
        'user': request.user,
        'default_avatars': default_avatars
    }
    return render(request, 'blog/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect')
            return redirect('profile')
        
        # Verify new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('profile')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Re-authenticate the user to prevent logout
        user = authenticate(username=request.user.username, password=new_password)
        login(request, user)
        
        messages.success(request, 'Password updated successfully!')
        return redirect('profile')
    
    return redirect('profile')

def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-date_posted')
    context = {
        'profile_user': user,
        'posts': posts,
    }
    return render(request, 'blog/user_profile.html', context)

@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.total_likes()
    })
