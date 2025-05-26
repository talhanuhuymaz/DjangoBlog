from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Profile

class Command(BaseCommand):
    help = 'Creates Profile objects for users that do not have one'

    def handle(self, *args, **options):
        users_without_profile = []
        
        # Find users without profiles
        for user in User.objects.all():
            try:
                # Try to access the profile
                profile = user.profile
            except Profile.DoesNotExist:
                users_without_profile.append(user)
        
        # Create profiles for users without one
        for user in users_without_profile:
            Profile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
        
        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users already have profiles.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profile)} user profiles.')) 