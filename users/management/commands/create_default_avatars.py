"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files import File
from users.avatar_models import AvatarCategory, AvatarOption
import os
import shutil
import tempfile
from pathlib import Path

class Command(BaseCommand):
    help = 'Creates default avatar categories and options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Recreate all avatar categories and options (warning: this will delete existing ones)',
        )

    def handle(self, *args, **options):
        recreate = options.get('recreate', False)
        
        if recreate:
            self.stdout.write(self.style.WARNING('Recreating all avatar categories and options...'))
            AvatarOption.objects.all().delete()
            AvatarCategory.objects.all().delete()
        
        # Create default categories
        categories = [
            {
                'name': 'Tech',
                'slug': 'tech',
                'description': 'Technology themed avatars',
                'display_order': 1,
            },
            {
                'name': 'Animals',
                'slug': 'animals',
                'description': 'Cute animal avatars',
                'display_order': 2,
            },
            {
                'name': 'Geometric',
                'slug': 'geometric',
                'description': 'Abstract geometric avatars',
                'display_order': 3,
            },
            {
                'name': 'Gaming',
                'slug': 'gaming',
                'description': 'Gaming themed avatars',
                'display_order': 4,
            },
            {
                'name': 'Space',
                'slug': 'space',
                'description': 'Space and cosmic themed avatars',
                'display_order': 5,
            },
            {
                'name': 'Abstract',
                'slug': 'abstract',
                'description': 'Abstract and artistic avatars',
                'display_order': 6,
            },
        ]
        
        # Create each category
        for cat_data in categories:
            category, created = AvatarCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))
        
        # Create placeholder default avatar
        self._create_placeholder_avatar()
        
        self.stdout.write(self.style.SUCCESS('Default avatar categories created successfully'))
    
    def _create_placeholder_avatar(self):
        """Creates a default placeholder avatar if none exists"""
        if AvatarOption.objects.filter(is_default=True).exists():
            self.stdout.write(self.style.WARNING('Default avatar already exists, skipping placeholder creation'))
            return
        
        # Get or create the Abstract category for the placeholder
        abstract_category, _ = AvatarCategory.objects.get_or_create(
            slug='abstract',
            defaults={
                'name': 'Abstract',
                'description': 'Abstract and artistic avatars',
                'display_order': 6,
            }
        )
        
        # Create a basic placeholder SVG
        svg_content = '''
        <svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
          <rect width="512" height="512" fill="#4e73df" />
          <circle cx="256" cy="186" r="120" fill="#ffffff" />
          <circle cx="256" cy="450" r="180" fill="#ffffff" />
        </svg>
        '''
        
        # Save the SVG to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as temp_file:
            temp_file.write(svg_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            # Create the default avatar option
            with open(temp_file_path, 'rb') as f:
                avatar = AvatarOption(
                    name='Default Avatar',
                    category=abstract_category,
                    is_default=True,
                    display_order=0
                )
                avatar.image.save('default_avatar.svg', File(f), save=True)
            
            self.stdout.write(self.style.SUCCESS('Created default placeholder avatar'))
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
