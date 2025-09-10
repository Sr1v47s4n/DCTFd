"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from users.avatar_models import AvatarCategory, AvatarOption
from users.models import BaseUser

class Command(BaseCommand):
    help = 'Debug user avatar information to identify profile image issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', 
            type=str,
            help='Username to check (optional)'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        self.stdout.write(self.style.SUCCESS('=== Avatar System Debug Information ==='))
        
        # List all avatar categories
        categories = AvatarCategory.objects.all()
        self.stdout.write(f"\nAvatar Categories ({categories.count()}):")
        for category in categories:
            avatar_count = category.avatars.count()
            self.stdout.write(f"  - {category.name} ({category.slug}): {avatar_count} avatars")
        
        # Show default avatar
        default_avatar = AvatarOption.objects.filter(is_default=True).first()
        if default_avatar:
            self.stdout.write(f"\nDefault Avatar: {default_avatar.name} (ID: {default_avatar.id}) from {default_avatar.category.name}")
        else:
            self.stdout.write(self.style.WARNING("\nNo default avatar is set in the system!"))
        
        # User information
        if username:
            try:
                user = BaseUser.objects.get(username=username)
                self.stdout.write(f"\nUser Avatar Information for {username}:")
                self.stdout.write(f"  - Selected Avatar ID: {user.avatar.id if user.avatar else 'None'}")
                self.stdout.write(f"  - Has Custom Avatar: {'Yes' if user.custom_avatar else 'No'}")
                self.stdout.write(f"  - Preferred Theme: {user.preferred_avatar_theme or 'None'}")
                self.stdout.write(f"  - Avatar URL: {user.avatar_url}")
            except BaseUser.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"\nUser with username '{username}' not found"))
        else:
            # Show sample of users with avatar stats
            users = BaseUser.objects.all()[:5]
            self.stdout.write(f"\nSample User Avatar Stats (showing {len(users)} of {BaseUser.objects.count()}):")
            for user in users:
                self.stdout.write(f"  - {user.username}: Avatar={user.avatar.id if user.avatar else 'None'}, Custom={bool(user.custom_avatar)}")
        
        self.stdout.write(self.style.SUCCESS('\nDebug information complete'))
