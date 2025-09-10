"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.conf import settings
import os

from users.avatar_models import AvatarCategory, AvatarOption


class Command(BaseCommand):
    help = 'Set up default avatars for the platform'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Setting up default avatars...'))
        self.setup_default_avatars()
        self.stdout.write(self.style.SUCCESS('Default avatars have been set up successfully!'))
    
    def setup_default_avatars(self):
        """Create default avatar categories and options"""
        # Create avatar directories if they don't exist
        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        
        # Create default category if it doesn't exist
        default_category, created = AvatarCategory.objects.get_or_create(
            slug='default',
            defaults={
                'name': 'Default',
                'description': 'Default system avatars',
                'display_order': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created avatar category: {default_category.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing avatar category: {default_category.name}'))
        
        # Create default placeholder avatars
        avatar_colors = [
            {'name': 'Default User', 'color': '#3498db', 'is_default': True, 'order': 1},
            {'name': 'Blue User', 'color': '#2980b9', 'is_default': False, 'order': 2},
            {'name': 'Green User', 'color': '#27ae60', 'is_default': False, 'order': 3},
            {'name': 'Red User', 'color': '#e74c3c', 'is_default': False, 'order': 4},
            {'name': 'Purple User', 'color': '#8e44ad', 'is_default': False, 'order': 5},
        ]
        
        # Generate and save each avatar
        for avatar_data in avatar_colors:
            avatar_name = avatar_data['name']
            
            # Check if avatar already exists
            if AvatarOption.objects.filter(name=avatar_name, category=default_category).exists():
                self.stdout.write(self.style.SUCCESS(f'Avatar already exists: {avatar_name}'))
                continue
                
            # Generate a simple SVG for the avatar
            color = avatar_data['color']
            svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
                <rect width="200" height="200" fill="{color}" />
                <text x="100" y="115" font-family="Arial" font-size="90" fill="white" text-anchor="middle">{avatar_name[0]}</text>
            </svg>"""
            
            # Create the avatar option
            avatar = AvatarOption(
                name=avatar_name,
                category=default_category,
                is_default=avatar_data['is_default'],
                display_order=avatar_data['order']
            )
            
            # Save the SVG as the avatar image
            avatar.image.save(f"{slugify(avatar_name)}.svg", ContentFile(svg_content.encode('utf-8')))
            
            self.stdout.write(self.style.SUCCESS(f'Created avatar: {avatar_name}'))
