"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.files.base import ContentFile
import datetime
import pytz
import os
import random
import sys
import traceback

from event.models import Event, EventSettings
from teams.models import Team
from core.models import GlobalSettings
from challenges.models import ChallengeCategory, Challenge, Flag
from users.avatar_models import AvatarCategory, AvatarOption

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up a development environment with default configurations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting development setup...'))
        
        # Check if any events already exist
        if Event.objects.exists():
            self.stdout.write(self.style.WARNING('Events already exist. Skipping setup.'))
            return
        
        try:
            # Create admin user
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin',  # Simple password for development
                    first_name='Admin',
                    last_name='User',
                    is_staff=True,
                    is_superuser=True,
                    type='admin'
                )
                self.stdout.write(self.style.SUCCESS('Created admin user with username: admin, password: admin'))
            else:
                admin_user = User.objects.get(username='admin')
                self.stdout.write(self.style.SUCCESS('Admin user already exists'))
            
            # Create a sample event
            now = timezone.now()
            start_time = now
            end_time = now + datetime.timedelta(days=7)
            registration_start = now - datetime.timedelta(days=1)
            registration_end = now + datetime.timedelta(days=5)
            
            event = Event.objects.create(
                name='Development CTF',
                short_description='A CTF environment for development purposes',
                description='This is an automatically created CTF environment for development purposes. You can use this to test features and functionality.',
                start_time=start_time,
                end_time=end_time,
                registration_start=registration_start,
                registration_end=registration_end,
                access='public',
                min_team_size=1,
                max_team_size=4,
                allow_individual_participants=True,
                created_by=admin_user,
                status='active'  # Set to active so development can proceed
            )
            
            # Create event settings
            event_settings = EventSettings.objects.create(
                event=event,
                theme='default',
                allow_zero_point_challenges=True,
                use_dynamic_scoring=True,
                require_email_verification=False,  # Disable for easier testing
                auto_approve_participants=True,  # Auto-approve for easier testing
                allow_team_creation=True,
                allow_team_joining=True,
                show_challenges_before_start=True,  # For easier development
                allow_challenge_feedback=True,
                enable_team_communication=True,
                enable_hints=True,
                submission_cooldown=5,  # 5 seconds
                max_submissions_per_minute=12
            )
            
            # Update global settings
            global_settings = GlobalSettings.get_settings()
            global_settings.site_name = 'DCTFd Development'
            global_settings.site_description = 'Development instance of DCTFd'
            global_settings.default_theme = 'default'
            
            # Set custom CSS for development mode indication
            custom_css = """
            /* Development mode indicator */
            body::before {
                content: 'Development Mode';
                position: fixed;
                bottom: 10px;
                right: 10px;
                background-color: #ff6b6b;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 9999;
                opacity: 0.8;
            }
            """
            global_settings.custom_css = custom_css
            global_settings.save()
            
            # Create sample categories
            categories = [
                'Web Exploitation',
                'Cryptography',
                'Reverse Engineering',
                'Binary Exploitation',
                'Forensics'
            ]
            
            category_objects = []
            for category_name in categories:
                # Check if the model accepts created_by
                try:
                    category = ChallengeCategory.objects.create(
                        name=category_name,
                        description=f'Sample challenges for {category_name}',
                        created_by=admin_user
                    )
                except TypeError as e:
                    # If created_by is not accepted, try without it
                    if 'created_by' in str(e):
                        category = ChallengeCategory.objects.create(
                            name=category_name,
                            description=f'Sample challenges for {category_name}'
                        )
                    # If another keyword error, try with minimal fields
                    elif 'got unexpected keyword arguments' in str(e):
                        category = ChallengeCategory.objects.create(
                            name=category_name,
                            description=f'Sample challenges for {category_name}'
                        )
                    else:
                        raise
                category_objects.append(category)
            
            # Create sample challenges
            challenge_data = [
                {
                    'name': 'Hello World',
                    'description': 'A starter challenge to get you familiar with flag submission.',
                    'category': category_objects[0],  # Web Exploitation
                    'value': 100,
                    'flag': 'flag{welcome_to_development_mode}'
                },
                {
                    'name': 'Basic Encryption',
                    'description': 'Can you decrypt this message? It was encrypted with a simple substitution cipher.',
                    'category': category_objects[1],  # Cryptography
                    'value': 200,
                    'flag': 'flag{cryptography_is_fun}'
                },
                {
                    'name': 'Simple Binary',
                    'description': 'Analyze this binary file to find the hidden flag.',
                    'category': category_objects[3],  # Binary Exploitation
                    'value': 300,
                    'flag': 'flag{binary_analysis_101}'
                }
            ]
            
            for data in challenge_data:
                # Check if the model accepts created_by
                try:
                    challenge = Challenge.objects.create(
                        name=data['name'],
                        description=data['description'],
                        category=data['category'],
                        value=data['value'],
                        state='visible',
                        event=event,
                        created_by=admin_user
                    )
                except TypeError as e:
                    # If created_by is not accepted, try without it
                    if 'created_by' in str(e):
                        challenge = Challenge.objects.create(
                            name=data['name'],
                            description=data['description'],
                            category=data['category'],
                            value=data['value'],
                            state='visible',
                            event=event
                        )
                    else:
                        raise
                
                # Create flag for the challenge
                try:
                    Flag.objects.create(
                        challenge=challenge,
                        flag=data['flag'],
                        type='static'
                    )
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating flag: {e}'))
                    raise
            
            # Create a sample team for testing
            team = Team.objects.create(
                name='Test Team',
                description='A team for testing purposes',
                event=event,
                captain=admin_user
            )
            
            self.stdout.write(self.style.SUCCESS('Development environment successfully set up!'))
            self.stdout.write(self.style.SUCCESS(f'Created event: {event.name}'))
            self.stdout.write(self.style.SUCCESS(f'Created {len(category_objects)} categories'))
            self.stdout.write(self.style.SUCCESS(f'Created {len(challenge_data)} sample challenges'))
            self.stdout.write(self.style.SUCCESS(f'Created test team: {team.name}'))
            
            # Set up default avatars
            self.setup_default_avatars()
            
            self.stdout.write(self.style.SUCCESS('Login with username: admin, password: admin'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during setup: {str(e)}'))
            traceback.print_exc()
            self.stdout.write(self.style.WARNING('Setup failed, but we can continue with partial configuration.'))
    
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
