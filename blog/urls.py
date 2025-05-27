from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home-page'),
    path('test/', views.test, name='test'),
    path('login/', views.login_view, name='login-page'),
    path('signup/', views.signup, name='signup'),
    path('newpost/', views.create_post, name='newpost'),
    path('myposts/', views.my_posts, name='my-posts'),
    path('signout/', views.signout, name='signout'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login-page'), name='logout'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('user/<str:username>/', views.profile_view, name='user_profile'),
    path('like/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('toggle_follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('get_notifications/', views.get_notifications, name='get_notifications'),
    path('mark_notifications_read/', views.mark_notifications_read, name='mark_notifications_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
