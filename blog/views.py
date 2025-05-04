from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages

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
            return redirect('home')  # You'll need to create this URL pattern later
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'blog/login.html')
