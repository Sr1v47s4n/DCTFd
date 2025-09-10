#!/usr/bin/env python
"""
Load avatars from media/avatars folder into the database.
"""

import os
import django
import glob
from django.conf import settings
from django.utils.text import slugify
from django.core.files import File

# Set up Django environment
os.environ.setdefault("DJANGO_ENVIRONMENT", "development")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DCTFd.settings')
django.setup()

from users.avatar_models import AvatarCategory, AvatarOption

def clean_existing_data():
    """Remove existing avatar data to start fresh"""
    print("Cleaning existing avatar data...")
    AvatarOption.objects.all().delete()
    AvatarCategory.objects.all().delete()
    print("Existing avatar data cleaned.")

def create_avatar_categories():
    """Create categories based on folder structure in media/avatars"""
    avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
    
    # Get all subdirectories
    categories = []
    
    # Add a default category first
    default_category = AvatarCategory.objects.create(
        name='Default',
        slug='default',
        description='Default system avatars',
        display_order=0
    )
    print(f"Created category: {default_category.name}")
    categories.append(default_category)
    
    # Then add categories from subdirectories
    subdirs = [d for d in os.listdir(avatar_dir) if os.path.isdir(os.path.join(avatar_dir, d))]
    
    for i, dir_name in enumerate(sorted(subdirs)):
        dir_path = os.path.join(avatar_dir, dir_name)
        
        # Clean up directory name for display
        category_name = dir_name.replace('_', ' ').title()
        category_slug = slugify(dir_name)
        
        # Skip if this category already exists
        if AvatarCategory.objects.filter(slug=category_slug).exists():
            print(f"Category already exists: {category_name}")
            category = AvatarCategory.objects.get(slug=category_slug)
            categories.append(category)
            continue
        
        category = AvatarCategory.objects.create(
            name=category_name,
            slug=category_slug,
            description=f'{category_name} avatars',
            display_order=i+1
        )
        print(f"Created category: {category.name}")
        categories.append(category)
    
    return categories

def load_avatars_from_directory(category, directory, max_avatars=8):
    """Load avatar images from a directory"""
    # Get all image files in the directory
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.svg']:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    # Skip text files and other non-image files
    image_files = [f for f in image_files if os.path.splitext(f)[1].lower() in ['.png', '.jpg', '.jpeg', '.svg']]
    
    # Limit the number of avatars per category
    image_files = image_files[:max_avatars]
    
    for i, image_path in enumerate(image_files):
        # Get just the filename without extension
        filename = os.path.basename(image_path)
        name = os.path.splitext(filename)[0]
        
        # Clean up the name for display
        display_name = name.replace('_', ' ').title()
        if len(display_name) > 30:  # Truncate very long names
            display_name = display_name[:30]
        
        try:
            with open(image_path, 'rb') as f:
                avatar = AvatarOption(
                    name=display_name,
                    category=category,
                    display_order=i+1,
                    is_default=True if i == 0 and category.name == 'Default' else False
                )
                avatar.image.save(filename, File(f), save=True)
                print(f"Added avatar: {category.name} - {avatar.name}")
        except Exception as e:
            print(f"Error adding avatar {filename}: {str(e)}")

def load_top_level_avatars(default_category):
    """Load avatars from the top level of the avatars directory"""
    avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
    
    # Get all image files in the top level directory
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.svg']:
        image_files.extend(glob.glob(os.path.join(avatar_dir, ext)))
    
    # Skip text files and other non-image files
    image_files = [f for f in image_files if os.path.splitext(f)[1].lower() in ['.png', '.jpg', '.jpeg', '.svg']]
    
    for i, image_path in enumerate(image_files):
        if os.path.isfile(image_path):
            # Get just the filename without extension
            filename = os.path.basename(image_path)
            name = os.path.splitext(filename)[0]
            
            # Clean up the name for display
            display_name = name.replace('_', ' ').title()
            if len(display_name) > 30:  # Truncate very long names
                display_name = display_name[:30]
            
            try:
                with open(image_path, 'rb') as f:
                    avatar = AvatarOption(
                        name=display_name,
                        category=default_category,
                        display_order=i+1,
                        is_default=True if i == 0 else False
                    )
                    avatar.image.save(filename, File(f), save=True)
                    print(f"Added avatar: {default_category.name} - {avatar.name}")
            except Exception as e:
                print(f"Error adding avatar {filename}: {str(e)}")

def main():
    """Main function to load avatar data"""
    print("Loading avatar data from existing files...")
    
    # Clean existing data
    clean_existing_data()
    
    # Create categories
    categories = create_avatar_categories()
    
    # Find default category
    default_category = AvatarCategory.objects.get(name='Default')
    
    # Load top-level avatars into the default category
    load_top_level_avatars(default_category)
    
    # Load avatars from each category directory
    avatar_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
    for category in categories:
        if category.name != 'Default':  # Skip default as we already processed it
            category_dir = os.path.join(avatar_dir, category.slug)
            if os.path.isdir(category_dir):
                load_avatars_from_directory(category, category_dir)
    
    # Set the first avatar as default if no default is set
    if not AvatarOption.objects.filter(is_default=True).exists():
        first_avatar = AvatarOption.objects.first()
        if first_avatar:
            first_avatar.is_default = True
            first_avatar.save()
            print(f"Set {first_avatar.name} as default avatar")
    
    # Print summary
    print(f"\nAvatar loading complete!")
    print(f"Total categories: {AvatarCategory.objects.count()}")
    print(f"Total avatars: {AvatarOption.objects.count()}")

if __name__ == '__main__':
    main()
