from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post

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
        
        if title and content:
            Post.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            messages.success(request, 'Post created successfully!')
            return redirect('home-page')
        else:
            messages.error(request, 'Please fill in all fields')
    
    return render(request, 'blog/new_post.html')

@login_required
def my_posts(request):
    context = {
        'posts': Post.objects.filter(author=request.user).order_by('-date_posted')
    }
    return render(request, 'blog/my_posts.html', context)
