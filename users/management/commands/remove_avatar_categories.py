"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from users.avatar_models import AvatarCategory, AvatarOption
import os

class Command(BaseCommand):
    help = 'Removes specified avatar categories and their associated avatars'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories', 
            nargs='+',
            type=str,
            help='List of category slugs to remove (space-separated)'
        )

    def handle(self, *args, **options):
        categories_to_remove = options.get('categories', [])
        if not categories_to_remove:
            self.stdout.write(self.style.WARNING('No categories specified for removal. Use --categories <slug1> <slug2> ...'))
            return
            
        for category_slug in categories_to_remove:
            try:
                category = AvatarCategory.objects.get(slug=category_slug)
                
                # Get list of all avatar image paths for this category
                avatar_images = []
                for avatar in category.avatars.all():
                    if avatar.image and hasattr(avatar.image, 'path'):
                        avatar_images.append(avatar.image.path)
                
                # Delete the avatars in this category
                avatar_count = category.avatars.count()
                category.avatars.all().delete()
                
                # Delete the category itself
                category_name = category.name
                category.delete()
                
                # Remove the image files
                for img_path in avatar_images:
                    if os.path.exists(img_path):
                        try:
                            os.remove(img_path)
                            self.stdout.write(f'  - Removed image file: {img_path}')
                        except OSError as e:
                            self.stdout.write(self.style.WARNING(f'  - Failed to remove image file: {img_path} - {e}'))
                
                self.stdout.write(self.style.SUCCESS(f'Successfully removed category "{category_name}" with {avatar_count} avatars'))
                
            except AvatarCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Category with slug "{category_slug}" does not exist'))
                
        self.stdout.write(self.style.SUCCESS('Avatar category removal complete'))
