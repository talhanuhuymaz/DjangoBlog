from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Profile, Comment, Notification
from django.conf import settings
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
import cloudinary
import cloudinary.uploader

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
            except Profile.DoesNotExist:
                # Create profile if it doesn't exist
                Profile.objects.create(user=user)
                
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
    active_tab = request.GET.get('tab', 'following')
    
    # Get posts for both tabs
    if search_query:
        all_posts = Post.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        ).order_by('-date_posted')
    else:
        all_posts = Post.objects.all().order_by('-date_posted')
    
    # Split posts into following and explore
    following_users = request.user.profile.following.all()
    following_posts = all_posts.filter(author__in=following_users)
    explore_posts = all_posts.exclude(author__in=following_users)
    
    # Get liked posts for the current user
    liked_posts = []
    if request.user.is_authenticated:
        liked_posts = Post.objects.filter(likes=request.user).values_list('id', flat=True)
    
    context = {
        'following_posts': following_posts,
        'explore_posts': explore_posts,
        'search_query': search_query,
        'liked_posts': liked_posts,
        'active_tab': active_tab
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
def settings(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        avatar = request.FILES.get('avatar')
        delete_avatar = request.POST.get('delete_avatar')
        
        # Verify password
        if not request.user.check_password(password):
            messages.error(request, 'Current password is incorrect')
            return redirect('settings')
        
        # Validate username and email
        if not username or not email:
            messages.error(request, 'Please fill in all required fields')
            return redirect('settings')
        
        try:
            # Update user information
            user = request.user
            user.username = username
            user.email = email
            user.save()
            
            # Handle avatar update
            if delete_avatar and user.profile.avatar:
                # Delete the image from Cloudinary
                if hasattr(user.profile.avatar, 'public_id'):
                    cloudinary.uploader.destroy(user.profile.avatar.public_id)
                user.profile.avatar = None
            elif avatar:
                # Validate file size (max 2MB)
                if avatar.size > 2 * 1024 * 1024:
                    messages.error(request, 'Avatar size should not exceed 2MB')
                    return redirect('settings')
                
                # Validate file type
                if not avatar.content_type.startswith('image/'):
                    messages.error(request, 'File must be an image')
                    return redirect('settings')
                
                # Delete old avatar from Cloudinary if it exists
                if user.profile.avatar and hasattr(user.profile.avatar, 'public_id'):
                    cloudinary.uploader.destroy(user.profile.avatar.public_id)
                
                # Upload new avatar
                user.profile.avatar = avatar
            
            user.profile.save()
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
        
        return redirect('settings')
    
    context = {
        'user': request.user
    }
    return render(request, 'blog/settings.html', context)

@login_required
def profile(request):
    # Get the user's posts
    posts = Post.objects.filter(author=request.user).order_by('-date_posted')
    
    # Get followers and following lists
    followers = User.objects.filter(profile__following=request.user).exclude(username='')
    following = request.user.profile.following.exclude(username='')
    
    context = {
        'profile_user': request.user,
        'posts': posts,
        'followers': followers,
        'following': following,
        'followers_count': request.user.profile.followers_count,
        'following_count': request.user.profile.following_count,
    }
    return render(request, 'blog/user_profile.html', context)

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
    try:
        user = get_object_or_404(User, username=username)
        
        # Ensure user has a profile
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=user)
        
        posts = Post.objects.filter(author=user).order_by('-date_posted')
        
        # Get followers and following lists, filtering out invalid users
        followers = User.objects.filter(profile__following=user).exclude(username='')
        following = user.profile.following.exclude(username='')
        
        # Get liked posts for the current user
        liked_posts = []
        if request.user.is_authenticated:
            liked_posts = Post.objects.filter(likes=request.user).values_list('id', flat=True)
        
        context = {
            'profile_user': user,
            'posts': posts,
            'followers': followers,
            'following': following,
            'followers_count': user.profile.followers_count,
            'following_count': user.profile.following_count,
            'liked_posts': liked_posts,
        }
        return render(request, 'blog/user_profile.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return redirect('home-page')

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
        # Create notification for the post author
        if request.user != post.author:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type=Notification.LIKE,
                post=post
            )
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.total_likes()
    })

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')
    
    if content:
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'date_posted': comment.date_posted.strftime("%B %d, %Y"),
                    'author_avatar_url': comment.author.profile.avatar.url if comment.author.profile.avatar else None,
                    'author_selected_avatar': comment.author.profile.selected_avatar,
                    'author_selected_avatar_color': comment.author.profile.selected_avatar_color,
                }
            })
        else:
            messages.success(request, 'Comment added successfully!')
            return redirect(f'{reverse_lazy("home-page")}?post={post.id}')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty!'}, status=400)
        else:
            messages.error(request, 'Comment cannot be empty!')
            return redirect(f'{reverse_lazy("home-page")}?post={post.id}')

@login_required
@require_POST
def delete_comment(request, comment_id):
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        
        if request.user == comment.author:
            post_id = comment.post.id  # Get the post ID before deleting the comment
            comment.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Comment deleted successfully!',
                    'post_id': post_id
                })
            else:
                messages.success(request, 'Comment deleted successfully!')
                return redirect(f'{reverse_lazy("home-page")}?post={post_id}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You can only delete your own comments!'
                }, status=403)
            else:
                messages.error(request, 'You can only delete your own comments!')
                return redirect('home-page')
    except Comment.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Comment not found'
            }, status=404)
        else:
            messages.error(request, 'Comment not found')
            return redirect('home-page')

@login_required
def toggle_follow(request, username):
    try:
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user == user_to_follow:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': "You cannot follow yourself!"
                }, status=400)
            messages.error(request, "You cannot follow yourself!")
            return redirect('home-page')
        
        # Ensure both users have profiles
        try:
            request.user.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=request.user)
            
        try:
            user_to_follow.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=user_to_follow)
        
        is_following = user_to_follow in request.user.profile.following.all()
        if is_following:
            request.user.profile.following.remove(user_to_follow)
            message = f"You have unfollowed {user_to_follow.username}"
        else:
            request.user.profile.following.add(user_to_follow)
            message = f"You are now following {user_to_follow.username}"
            # Create notification for the followed user
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type=Notification.FOLLOW
            )
        
        # If the request is AJAX, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': message,
                'is_following': not is_following,
                'followers_count': user_to_follow.profile.followers_count,
                'following_count': user_to_follow.profile.following_count
            })
        
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'home-page'))
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        messages.error(request, f'Error following user: {str(e)}')
        return redirect('home-page')

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None:
            # Delete the user's profile first (if it exists)
            if hasattr(user, 'profile'):
                user.profile.delete()
            
            # Delete all user's posts
            user.post_set.all().delete()
            
            # Delete all user's comments
            user.comment_set.all().delete()
            
            # Delete the user account
            user.delete()
            
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('login-page')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('settings')
    
    return redirect('settings')

@login_required
def get_notifications(request):
    notifications = request.user.notifications.all()[:10]  # Get last 10 notifications
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    notifications_data = []
    for notification in notifications:
        data = {
            'id': notification.id,
            'sender': notification.sender.username,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime("%b %d, %Y, %I:%M %p"),
            'is_read': notification.is_read,
        }
        if notification.post:
            data['post_id'] = notification.post.id
            data['post_title'] = notification.post.title
        notifications_data.append(data)
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@login_required
@require_POST
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})
