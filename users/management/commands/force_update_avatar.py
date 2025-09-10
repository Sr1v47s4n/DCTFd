"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from users.models import BaseUser
from users.avatar_models import AvatarOption
import sys

class Command(BaseCommand):
    help = 'Force update a user avatar to fix avatar selection issues'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to update')
        parser.add_argument('avatar_id', type=int, help='ID of the avatar to assign')
        
    def handle(self, *args, **options):
        username = options['username']
        avatar_id = options['avatar_id']
        
        try:
            user = BaseUser.objects.get(username=username)
        except BaseUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
            sys.exit(1)
        
        try:
            avatar = AvatarOption.objects.get(id=avatar_id)
        except AvatarOption.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Avatar with ID {avatar_id} not found"))
            sys.exit(1)
        
        # Store original avatar info for reporting
        old_avatar_id = user.avatar.id if user.avatar else None
        old_avatar_name = user.avatar.name if user.avatar else "None"
        
        # Force update the avatar
        user.avatar = avatar
        user.save(update_fields=['avatar'])
        
        # Report success
        self.stdout.write(self.style.SUCCESS(f"Successfully updated avatar for user '{username}'"))
        self.stdout.write(f"Old avatar: {old_avatar_id} ({old_avatar_name})")
        self.stdout.write(f"New avatar: {avatar.id} ({avatar.name})")
        self.stdout.write(f"Avatar URL: {user.get_avatar_url()}")
