from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.login_view, name='login-page'),
    path('home/', views.home, name='home-page'),
    path('newpost/', views.new_post, name='newpost'),
    path('myposts/', views.my_posts, name='my-posts'),
    path('signup/', views.signup, name='signup-page'),
    path('signout/', views.signout, name='signout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login-page'), name='logout'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('test-image/<str:image_name>/', views.test_image, name='test_image'),
]
