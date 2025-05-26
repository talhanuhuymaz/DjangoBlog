from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login-page'),
    path('home/', views.home, name='home-page'),
    path('newpost/', views.new_post, name='newpost'),
    path('myposts/', views.my_posts, name='my-posts'),
    path('signup/', views.signup, name='signup-page'),
    path('signout/', views.signout, name='signout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login-page'), name='logout'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('like/', views.like_post, name='like-post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('toggle_follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('delete-account/', views.delete_account, name='delete_account'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
