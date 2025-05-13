from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.signup, name='signup-page'),
    path('login/', views.login_view, name='login-page'),
    path('home/', views.home, name='home-page'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login-page'), name='logout'),
    path('new-post/', views.new_post, name='new-post'),
    path('my-posts/', views.my_posts, name='my-posts'),
]
