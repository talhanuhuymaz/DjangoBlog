from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post
from django.conf import settings
import os

# Create your views here.
def test(request):
    return render(request,'blog/base.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('upassword')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
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

@login_required
def home(request):
    context = {
        'posts': Post.objects.all().order_by('-date_posted')
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
                    post.image = image
                    post.save()
                    print(f"Image saved at: {post.image.url}")  # Debug print
                
                messages.success(request, 'Post created successfully!')
                return redirect('home-page')
            except Exception as e:
                print(f"Error saving post: {str(e)}")
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

def test_image(request, image_name):
    image_path = os.path.join(settings.MEDIA_ROOT, 'post_images', image_name)
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            return HttpResponse(img.read(), content_type='image/jpeg')
    return HttpResponse('Image not found', status=404)
