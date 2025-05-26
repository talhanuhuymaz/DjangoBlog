from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='post_likes', blank=True)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def delete(self, *args, **kwargs):
        # Delete the image file when the post is deleted
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    selected_avatar = models.CharField(max_length=50, null=True, blank=True)
    selected_avatar_color = models.CharField(max_length=7, default='#4F46E5')

    def __str__(self):
        return f'{self.user.username} Profile'

    def delete(self, *args, **kwargs):
        # Delete the image file when the profile is deleted
        if self.avatar:
            self.avatar.delete()
        super().delete(*args, **kwargs)

# Create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Save profile when user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
