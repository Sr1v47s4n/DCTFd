"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

"""
Management command to populate the database with comprehensive sample data
"""
import random
import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import transaction

# Import all necessary models
from users.models import BaseUser
from event.models import Event, EventSettings
from teams.models import Team
from challenges.models import Challenge, ChallengeCategory, Submission, Hint, Flag, ChallengeFile
from core.custom_fields import CustomFieldDefinition, CustomFieldValue

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with comprehensive sample data for DCTFd'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            help='Delete all existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['delete_existing']:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            self.delete_existing_data()

        self.stdout.write(self.style.SUCCESS('Creating comprehensive sample data...'))
        
        with transaction.atomic():
            # Create sample data in order
            admins = self.create_admin_users()
            events = self.create_events(admins)
            custom_fields = self.create_custom_fields(events)
            categories = self.create_categories(events)
            challenges = self.create_challenges(categories, events)
            flags = self.create_flags(challenges)
            hints = self.create_hints(challenges)
            users = self.create_users(events, custom_fields)
            teams = self.create_teams(users, events, custom_fields)
            submissions = self.create_submissions(users, teams, challenges)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(admins)} Admin Users\n'
                f'- {len(events)} Events\n'
                f'- {len(custom_fields)} Custom Fields\n'
                f'- {len(categories)} Categories\n'
                f'- {len(challenges)} Challenges\n'
                f'- {len(flags)} Flags\n'
                f'- {len(hints)} Hints\n'
                f'- {len(users)} Users\n'
                f'- {len(teams)} Teams\n'
                f'- {len(submissions)} Submissions'
            )
        )
        
        # Print final credentials summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🔐 COMPLETE LOGIN CREDENTIALS SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        self.stdout.write(self.style.SUCCESS('\n🔑 SUPERUSER ACCESS:'))
        self.stdout.write('   Username: admin | Password: admin123')
        
        self.stdout.write(self.style.SUCCESS('\n👥 ORGANIZER ACCOUNTS:'))
        self.stdout.write('   Username: organizer1 | Password: organizer123')
        self.stdout.write('   Username: organizer2 | Password: organizer123') 
        self.stdout.write('   Username: organizer3 | Password: organizer123')
        
        self.stdout.write(self.style.SUCCESS('\n⚖️  STAFF ACCOUNTS:'))
        self.stdout.write('   Username: moderator1 | Password: staff123')
        self.stdout.write('   Username: judge1 | Password: staff123')
        
        self.stdout.write(self.style.SUCCESS('\n🎯 SAMPLE USER ACCOUNTS (all password: user123):'))
        sample_users = ['alice_hacker', 'bob_security', 'charlie_crypto', 'diana_detective']
        for username in sample_users:
            self.stdout.write(f'   Username: {username} | Password: user123')
        self.stdout.write(f'   ... and {len(users) - len(sample_users)} more users')
        
        self.stdout.write(self.style.SUCCESS('\n🏆 TEAM ACCESS:'))
        self.stdout.write('   Teams: CyberNinjas, SecureCoders, HackMasters, DigitalDefenders')
        self.stdout.write('   (Login with any team member and access team dashboard)')
        
        self.stdout.write(self.style.SUCCESS('\n📊 QUICK ACCESS URLs:'))
        self.stdout.write('   Admin Panel: /admin/')
        self.stdout.write('   Organizer Dashboard: /organizer/')
        self.stdout.write('   Main Platform: /')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Database fully populated and ready for testing!'))
        self.stdout.write(self.style.SUCCESS('='*60))

    def delete_existing_data(self):
        """Delete all existing data"""
        models_to_clear = [
            Submission, Hint, Flag, ChallengeFile, Challenge, ChallengeCategory, Team, CustomFieldValue, 
            CustomFieldDefinition, Event, EventSettings, BaseUser
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'Deleted {count} {model.__name__} records')

    def create_admin_users(self):
        """Create sample admin users"""
        admins = []
        
        self.stdout.write(self.style.SUCCESS('\n=== ADMIN & STAFF CREDENTIALS ==='))
        
        # Main admin
        admin_user = BaseUser.objects.create_user(
            username='admin',
            email='admin@dctfd.com',
            password='admin123',
            first_name='Super',
            last_name='Admin',
            phone='+15550001',
            is_staff=True,
            is_superuser=True,
            email_verified=True,
            type='admin'
        )
        admins.append(admin_user)
        self.stdout.write(f'🔑 SUPERUSER - Username: admin | Password: admin123 | Email: admin@dctfd.com')
        
        # Create organizer accounts
        organizer_data = [
            {
                'username': 'organizer1',
                'email': 'organizer1@dctfd.com',
                'first_name': 'John',
                'last_name': 'Organizer',
                'phone': '+15550002'
            },
            {
                'username': 'organizer2', 
                'email': 'organizer2@dctfd.com',
                'first_name': 'Jane',
                'last_name': 'Manager',
                'phone': '+15550003'
            },
            {
                'username': 'organizer3',
                'email': 'organizer3@dctfd.com', 
                'first_name': 'Mike',
                'last_name': 'Director',
                'phone': '+15550004'
            }
        ]
        
        for data in organizer_data:
            user = BaseUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='organizer123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                is_staff=True,
                email_verified=True,
                type='organizer'
            )
            admins.append(user)
            self.stdout.write(f'👤 ORGANIZER - Username: {data["username"]} | Password: organizer123 | Email: {data["email"]}')
        
        # Create additional staff roles
        staff_data = [
            {
                'username': 'moderator1',
                'email': 'moderator1@dctfd.com',
                'first_name': 'Sarah',
                'last_name': 'Moderator',
                'phone': '+15550005',
                'type': 'moderator'
            },
            {
                'username': 'judge1',
                'email': 'judge1@dctfd.com', 
                'first_name': 'David',
                'last_name': 'Judge',
                'phone': '+15550006',
                'type': 'judge'
            }
        ]
        
        for data in staff_data:
            user = BaseUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='staff123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                is_staff=True,
                email_verified=True,
                type=data['type']
            )
            admins.append(user)
            self.stdout.write(f'⚖️  {data["type"].upper()} - Username: {data["username"]} | Password: staff123 | Email: {data["email"]}')
            
        self.stdout.write(f'Created {len(admins)} admin users')
        return admins

    def create_events(self, admins):
        """Create sample events"""
        events = []
        
        # Get existing event or create one
        existing_event = Event.objects.first()
        if existing_event:
            events.append(existing_event)
            self.stdout.write(f'Using existing event: {existing_event.name}')
            
            # Create event settings if they don't exist
            if not hasattr(existing_event, 'settings'):
                EventSettings.objects.create(
                    event=existing_event,
                    allow_team_creation=True,
                    auto_approve_participants=True,
                    enable_user_custom_fields=True,
                    enable_team_custom_fields=True
                )
        else:
            # Use the event name from settings
            from django.conf import settings
            from django.utils.text import slugify
            event = Event.objects.create(
                name=settings.EVENT_NAME,
                slug=slugify(settings.EVENT_NAME),
                description=f'{settings.EVENT_NAME} CTF Event',
                short_description=f'{settings.EVENT_NAME} CTF Event',
                start_time=timezone.now() - timedelta(days=1),
                end_time=timezone.now() + timedelta(days=7),
                registration_start=timezone.now() - timedelta(days=10),
                registration_end=timezone.now() + timedelta(days=2),
                status='running',
                is_visible=True,
                created_by=admins[0]  # admin
            )
            
            # Create event settings
            EventSettings.objects.create(
                event=event,
                allow_team_creation=True,
                auto_approve_participants=True,
                enable_user_custom_fields=True,
                enable_team_custom_fields=True
            )
            events.append(event)
            self.stdout.write(f'Created event: {event.name}')
            
        self.stdout.write(f'Using {len(events)} events')
        return events

    def create_custom_fields(self, events):
        """Create sample custom fields"""
        custom_fields = []
        event_content_type = ContentType.objects.get_for_model(Event)
        
                # Custom fields for a single event
        event = events[0]
        
        # User custom fields for a single event
        user_field1 = CustomFieldDefinition.objects.create(
            content_type=event_content_type,
            object_id=event.id,
            field_for='user',
            field_type='text',
            label='Discord Username',
            description='Your Discord username for team communication',
            placeholder='e.g., username#1234',
            required=False,
            order=1
        )
        custom_fields.append(user_field1)
        
        user_field2 = CustomFieldDefinition.objects.create(
            content_type=event_content_type,
            object_id=event.id,
            field_for='user',
            field_type='select',
            label='T-Shirt Size',
            description='T-shirt size for event swag',
            options='XS\\nS\\nM\\nL\\nXL\\nXXL',
            required=False,
            order=2
        )
        custom_fields.append(user_field2)
        
        user_field3 = CustomFieldDefinition.objects.create(
            content_type=event_content_type,
            object_id=event.id,
            field_for='user',
            field_type='textarea',
            label='Dietary Requirements',
            description='Any dietary restrictions or allergies (for catering)',
            placeholder='e.g., Vegetarian, Gluten-free, No nuts',
            required=False,
            order=3
        )
        custom_fields.append(user_field3)
        
        # Team custom fields
        team_field1 = CustomFieldDefinition.objects.create(
            content_type=event_content_type,
            object_id=event.id,
            field_for='team',
            field_type='text',
            label='Institution Name',
            description='Name of your school, university, or organization',
            placeholder='e.g., MIT, Google, Harvard University',
            required=True,
            order=1
        )
        custom_fields.append(team_field1)
        
        team_field2 = CustomFieldDefinition.objects.create(
            content_type=event_content_type,
            object_id=event.id,
            field_for='team',
            field_type='select',
            label='Team Category',
            description='Select your team category',
            options='High School\\nUndergraduate\\nGraduate\\nProfessional\\nOpen',
            required=True,
            order=2
        )
        custom_fields.append(team_field2)
        
        self.stdout.write(f'Created {len(custom_fields)} custom fields')
        return custom_fields

    def create_categories(self, events):
        """Create challenge categories"""
        categories = []
        
        category_data = [
            {'name': 'Web Exploitation', 'description': 'Web application security challenges', 'color': '#e74c3c', 'order': 1},
            {'name': 'Cryptography', 'description': 'Encryption and decryption challenges', 'color': '#3498db', 'order': 2},
            {'name': 'Forensics', 'description': 'Digital forensics and analysis', 'color': '#2ecc71', 'order': 3},
            {'name': 'Reverse Engineering', 'description': 'Binary analysis and reverse engineering', 'color': '#9b59b6', 'order': 4},
            {'name': 'Pwn', 'description': 'Binary exploitation and buffer overflows', 'color': '#f39c12', 'order': 5},
            {'name': 'Steganography', 'description': 'Hidden message and data challenges', 'color': '#1abc9c', 'order': 6},
            {'name': 'OSINT', 'description': 'Open source intelligence gathering', 'color': '#34495e', 'order': 7},
            {'name': 'Misc', 'description': 'Miscellaneous challenges', 'color': '#95a5a6', 'order': 8}
        ]
        
        # Create categories only once (they're global)
        for cat_data in category_data:
            category, created = ChallengeCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color'],
                    'order': cat_data['order']
                }
            )
            categories.append(category)
        
        self.stdout.write(f'Created {len(categories)} categories')
        return categories

    def create_challenges(self, categories, events):
        """Create sample challenges"""
        challenges = []
        
        # Get current event
        current_event = events[0]
        
        challenge_data = [
            # Web Exploitation
            {
                'name': 'Login Bypass',
                'description': 'Can you bypass the login form? The admin credentials are hidden somewhere.\n\nFlag format: flag{...}',
                'category': 'Web Exploitation',
                'value': 100,
                'difficulty': 2
            },
            {
                'name': 'File Upload Vulnerability',
                'description': 'This web application allows file uploads. Can you exploit it to get the flag?\n\nURL: http://challenge.dctfd.com:8080/upload\n\nFlag format: flag{...}',
                'category': 'Web Exploitation',
                'value': 250,
                'difficulty': 3
            },
            {
                'name': 'Advanced XSS',
                'description': 'This application has a sophisticated XSS filter. Can you bypass it and steal the admin cookie?\n\nURL: http://challenge.dctfd.com:8081/xss\n\nFlag format: flag{...}',
                'category': 'Web Exploitation', 
                'value': 400,
                'difficulty': 4
            },
            
            # Cryptography
            {
                'name': 'Caesar Cipher',
                'description': 'Decode this message encrypted with Caesar cipher:\n\nCiphertext: IODJ{FDHVDU_FLSKHU_LV_HDVB}\n\nFlag format: flag{...}',
                'category': 'Cryptography',
                'value': 50,
                'difficulty': 1
            },
            {
                'name': 'RSA Factorization',
                'description': 'Factor this RSA modulus to decrypt the message:\n\nn = 1073676287\ne = 65537\nc = 963140665\n\nFlag format: flag{...}',
                'category': 'Cryptography',
                'value': 300,
                'difficulty': 3
            },
            
            # Forensics
            {
                'name': 'Hidden in Plain Sight',
                'description': 'There\'s something hidden in this image file. Can you find it?\n\nDownload: http://challenge.dctfd.com/files/image.png\n\nFlag format: flag{...}',
                'category': 'Forensics',
                'value': 150,
                'difficulty': 2
            },
            {
                'name': 'Memory Dump Analysis',
                'description': 'Analyze this memory dump to find the password:\n\nDownload: http://challenge.dctfd.com/files/memory.dmp\n\nFlag format: flag{...}',
                'category': 'Forensics',
                'value': 350,
                'difficulty': 4
            },
            
            # Reverse Engineering
            {
                'name': 'Simple Keygen',
                'description': 'Reverse engineer this binary to generate a valid license key:\n\nDownload: http://challenge.dctfd.com/files/keygen.exe\n\nFlag format: flag{...}',
                'category': 'Reverse Engineering',
                'value': 200,
                'difficulty': 3
            },
            
            # Pwn
            {
                'name': 'Buffer Overflow Basic',
                'description': 'Exploit this vulnerable C program:\n\nnc challenge.dctfd.com 9999\n\nSource code available at: http://challenge.dctfd.com/files/vuln.c\n\nFlag format: flag{...}',
                'category': 'Pwn',
                'value': 300,
                'difficulty': 4
            },
            
            # Steganography
            {
                'name': 'Secret Message',
                'description': 'There\'s a secret message hidden in this audio file:\n\nDownload: http://challenge.dctfd.com/files/secret.wav\n\nFlag format: flag{...}',
                'category': 'Steganography',
                'value': 180,
                'difficulty': 2
            },
            
            # OSINT
            {
                'name': 'Social Media Investigation',
                'description': 'Find information about this person using only public sources:\n\nUsername: cyber_detective_2025\n\nWhat\'s their favorite programming language?\n\nFlag format: flag{language_name}',
                'category': 'OSINT',
                'value': 120,
                'difficulty': 2
            },
            
            # Misc
            {
                'name': 'QR Code Challenge',
                'description': 'Decode this QR code to get the flag:\n\nDownload: http://challenge.dctfd.com/files/qrcode.png\n\nFlag format: flag{...}',
                'category': 'Misc',
                'value': 75,
                'difficulty': 1
            }
        ]
        
        for i, chal_data in enumerate(challenge_data):
            # Find category
            category = next((cat for cat in categories if cat.name == chal_data['category']), None)
            if not category:
                continue
                
            challenge = Challenge.objects.create(
                name=chal_data['name'],
                description=chal_data['description'],
                category=category,
                event=current_event,
                value=chal_data['value'],
                difficulty=chal_data['difficulty'],
                is_visible=True,
                max_attempts=0  # Unlimited attempts
            )
            challenges.append(challenge)
        
        self.stdout.write(f'Created {len(challenges)} challenges')
        return challenges

    def create_flags(self, challenges):
        """Create flags for challenges"""
        flags = []
        
        # Flag data for specific challenges
        flag_data = {
            'Login Bypass': [
                {'flag': 'flag{sql_injection_admin_bypass}', 'type': 'static'},
                {'flag': 'flag{admin_password_is_123456}', 'type': 'static'}
            ],
            'File Upload Vulnerability': [
                {'flag': 'flag{php_shell_uploaded_successfully}', 'type': 'static'}
            ],
            'XSS Filter Bypass': [
                {'flag': 'flag{xss_cookie_stolen_admin}', 'type': 'static'}
            ],
            'Caesar Cipher': [
                {'flag': 'flag{caesar_cipher_is_easy}', 'type': 'static'}
            ],
            'RSA Factorization': [
                {'flag': 'flag{rsa_factored_primes_found}', 'type': 'static'}
            ],
            'Image Steganography': [
                {'flag': 'flag{hidden_data_in_pixels}', 'type': 'static'}
            ],
            'Memory Analysis': [
                {'flag': 'flag{password_found_in_memory}', 'type': 'static'}
            ],
            'Binary Reverse Engineering': [
                {'flag': 'flag{license_key_algorithm_cracked}', 'type': 'static'}
            ],
            'Buffer Overflow': [
                {'flag': 'flag{stack_overflow_exploit_success}', 'type': 'static'}
            ],
            'Social Media Investigation': [
                {'flag': 'flag{python}', 'type': 'static'},
                {'flag': 'flag{java}', 'type': 'static'},
                {'flag': 'flag{javascript}', 'type': 'static'}
            ],
            'QR Code Challenge': [
                {'flag': 'flag{qr_code_decoded_successfully}', 'type': 'static'}
            ]
        }
        
        # Create flags for specific challenges
        for challenge in challenges:
            if challenge.name in flag_data:
                for flag_info in flag_data[challenge.name]:
                    flag = Flag.objects.create(
                        challenge=challenge,
                        flag=flag_info['flag'],
                        type=flag_info['type']
                    )
                    flags.append(flag)
            else:
                # Create a default flag for challenges without specific flags
                default_flag = f"flag{{{challenge.name.lower().replace(' ', '_').replace('-', '_')}}}"
                flag = Flag.objects.create(
                    challenge=challenge,
                    flag=default_flag,
                    type='static'
                )
                flags.append(flag)
        
        # Add some regex flags for advanced challenges
        advanced_challenges = [c for c in challenges if c.difficulty >= 4]
        for challenge in advanced_challenges[:3]:  # Add regex flags to first 3 advanced challenges
            regex_flag = Flag.objects.create(
                challenge=challenge,
                flag=r'flag\{[a-z0-9_]+\}',
                type='regex'
            )
            flags.append(regex_flag)
        
        self.stdout.write(f'Created {len(flags)} flags')
        return flags

    def create_hints(self, challenges):
        """Create hints for challenges"""
        hints = []
        
        # Add hints to some challenges
        hint_data = [
            {
                'challenge_name': 'Login Bypass',
                'hints': [
                    'Think about common SQL injection techniques',
                    'Try using OR statements in the username field'
                ]
            },
            {
                'challenge_name': 'File Upload Vulnerability',
                'hints': [
                    'What file types are allowed?',
                    'Can you upload a PHP file?',
                    'Try renaming your file extension'
                ]
            },
            {
                'challenge_name': 'Caesar Cipher',
                'hints': [
                    'Caesar cipher shifts each letter by a fixed number',
                    'Try different shift values'
                ]
            },
            {
                'challenge_name': 'RSA Factorization',
                'hints': [
                    'The modulus n is the product of two primes',
                    'Try factoring n using online tools or write a script'
                ]
            }
        ]
        
        for hint_info in hint_data:
            challenge = next((c for c in challenges if c.name == hint_info['challenge_name']), None)
            if challenge:
                for i, hint_text in enumerate(hint_info['hints']):
                    hint = Hint.objects.create(
                        challenge=challenge,
                        content=hint_text,
                        cost=(i + 1) * 25  # 25, 50, 75 points
                    )
                    hints.append(hint)
        
        self.stdout.write(f'Created {len(hints)} hints')
        return hints

    def create_users(self, events, custom_fields):
        """Create sample users"""
        users = []
        current_event = events[0]
        
        self.stdout.write(self.style.SUCCESS('\n=== REGULAR USER CREDENTIALS ==='))
        
        # Get user custom fields for current event
        user_custom_fields = [cf for cf in custom_fields if cf.field_for == 'user' and cf.object_id == current_event.id]
        
        user_data = [
            {'username': 'alice_hacker', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson', 'country': 'US', 'skill': 'expert'},
            {'username': 'bob_security', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith', 'country': 'CA', 'skill': 'intermediate'},
            {'username': 'charlie_crypto', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown', 'country': 'GB', 'skill': 'advanced'},
            {'username': 'diana_detective', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Wilson', 'country': 'AU', 'skill': 'expert'},
            {'username': 'eve_exploit', 'email': 'eve@example.com', 'first_name': 'Eve', 'last_name': 'Davis', 'country': 'DE', 'skill': 'advanced'},
            {'username': 'frank_forensics', 'email': 'frank@example.com', 'first_name': 'Frank', 'last_name': 'Miller', 'country': 'FR', 'skill': 'intermediate'},
            {'username': 'grace_pwn', 'email': 'grace@example.com', 'first_name': 'Grace', 'last_name': 'Lee', 'country': 'KR', 'skill': 'expert'},
            {'username': 'henry_rev', 'email': 'henry@example.com', 'first_name': 'Henry', 'last_name': 'Taylor', 'country': 'JP', 'skill': 'beginner'},
            {'username': 'iris_osint', 'email': 'iris@example.com', 'first_name': 'Iris', 'last_name': 'Chen', 'country': 'CN', 'skill': 'intermediate'},
            {'username': 'jack_misc', 'email': 'jack@example.com', 'first_name': 'Jack', 'last_name': 'Anderson', 'country': 'IN', 'skill': 'advanced'},
            {'username': 'kate_web', 'email': 'kate@example.com', 'first_name': 'Kate', 'last_name': 'Martinez', 'country': 'ES', 'skill': 'beginner'},
            {'username': 'leo_stego', 'email': 'leo@example.com', 'first_name': 'Leo', 'last_name': 'Garcia', 'country': 'MX', 'skill': 'intermediate'},
        ]
        
        skill_icons = {
            'beginner': '🌱',
            'intermediate': '🚀', 
            'advanced': '⭐',
            'expert': '👑'
        }
        
        for i, data in enumerate(user_data):
            # Generate unique phone number for each user
            unique_phone = f'+1555{1000 + i:04d}'
            
            user = BaseUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='user123',
                first_name=data['first_name'],
                last_name=data['last_name'],
                country=data['country'],
                phone=unique_phone,
                gender=random.choice(['M', 'F', 'O']),
                email_verified=True
            )
            users.append(user)
            
            # Print credentials with skill level
            skill = data.get('skill', 'intermediate')
            self.stdout.write(f'{skill_icons[skill]} USER ({skill.upper()}) - Username: {data["username"]} | Password: user123 | Email: {data["email"]}')
            
            # Add custom field values for current event users
            if user_custom_fields:
                user_content_type = ContentType.objects.get_for_model(BaseUser)
                
                for custom_field in user_custom_fields:
                    if custom_field.label == 'Student ID':
                        value = f'2025{random.randint(100000, 999999)}'
                    elif custom_field.label == 'Experience Level':
                        value = skill.title()
                    elif custom_field.label == 'Dietary Requirements':
                        value = random.choice(['None', 'Vegetarian', 'Vegan', 'Gluten-free', 'No nuts'])
                    else:
                        continue
                        
                    CustomFieldValue.objects.create(
                        field_definition=custom_field,
                        content_type=user_content_type,
                        object_id=user.id,
                        value=value
                    )
        
        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_teams(self, users, events, custom_fields):
        """Create sample teams"""
        teams = []
        current_event = events[0]
        
        # Get team custom fields for current event
        team_custom_fields = [cf for cf in custom_fields if cf.field_for == 'team' and cf.object_id == current_event.id]
        
        team_data = [
            {
                'name': 'CyberGuardians',
                'description': 'Elite cybersecurity team focused on web exploitation and cryptography.',
                'members': users[0:3],  # Alice, Bob, Charlie
                'captain': users[0],
                'country': 'US',
                'affiliation': 'MIT'
            },
            {
                'name': 'SecurityNinjas', 
                'description': 'Stealthy hackers specializing in forensics and reverse engineering.',
                'members': users[3:6],  # Diana, Eve, Frank
                'captain': users[3],
                'country': 'CA',
                'affiliation': 'University of Toronto'
            },
            {
                'name': 'DigitalDetectives',
                'description': 'Investigative team excelling in OSINT and steganography challenges.',
                'members': users[6:9],  # Grace, Henry, Iris
                'captain': users[6],
                'country': 'GB',
                'affiliation': 'Oxford University'
            },
            {
                'name': 'PwnMasters',
                'description': 'Binary exploitation specialists and pwn challenge solvers.',
                'members': users[9:12],  # Jack, Kate, Leo
                'captain': users[9],
                'country': 'DE',
                'affiliation': 'Technical University Munich'
            }
        ]
        
        for team_info in team_data:
            team = Team.objects.create(
                name=team_info['name'],
                description=team_info['description'],
                captain=team_info['captain'],
                country=team_info['country'],
                affiliation=team_info['affiliation'],
                score=0
            )
            
            # Add members to team
            for member in team_info['members']:
                member.team = team
                member.save()
            
            teams.append(team)
            
            # Add custom field values for teams
            if team_custom_fields:
                team_content_type = ContentType.objects.get_for_model(Team)
                
                for custom_field in team_custom_fields:
                    if custom_field.label == 'Institution Name':
                        value = team_info['affiliation']
                    elif custom_field.label == 'Team Category':
                        value = random.choice(['Undergraduate', 'Graduate', 'Professional', 'Open'])
                    else:
                        continue
                        
                    CustomFieldValue.objects.create(
                        field_definition=custom_field,
                        content_type=team_content_type,
                        object_id=team.id,
                        value=value
                    )
        
        self.stdout.write(f'Created {len(teams)} teams')
        return teams

    def create_submissions(self, users, teams, challenges):
        """Create sample submissions with proper flags and scoring"""
        submissions = []
        current_challenges = [c for c in challenges if c.event.status == 'registration']
        
        # Create realistic submission patterns
        solved_challenges = set()
        
        # Team performance levels (some teams are better than others)
        team_skill_levels = {
            team: random.choice(['beginner', 'intermediate', 'advanced', 'expert']) 
            for team in teams
        }
        
        # Create submissions over time
        for hour in range(72):  # 3 days of submissions
            submission_time = timezone.now() - timedelta(hours=72-hour)
            
            # Some teams are more active at certain times
            active_teams = random.sample(teams, random.randint(1, len(teams)//2 + 1))
            
            for team in active_teams:
                # Each team attempts some challenges
                num_attempts = random.randint(0, 3)
                
                for _ in range(num_attempts):
                    # Choose challenge based on team skill level
                    skill = team_skill_levels[team]
                    if skill == 'beginner':
                        available_challenges = [c for c in current_challenges if c.difficulty <= 2]
                    elif skill == 'intermediate':
                        available_challenges = [c for c in current_challenges if c.difficulty <= 3]
                    elif skill == 'advanced':
                        available_challenges = [c for c in current_challenges if c.difficulty <= 4]
                    else:  # expert
                        available_challenges = current_challenges
                    
                    if not available_challenges:
                        continue
                        
                    challenge = random.choice(available_challenges)
                    user = random.choice(team.members.all()) if team.members.exists() else team.captain
                    
                    # Check if team already solved this challenge
                    if (team, challenge) in solved_challenges:
                        continue
                    
                    # Get actual flags for this challenge
                    challenge_flags = challenge.flags.all()
                    if not challenge_flags:
                        continue
                    
                    # Determine if submission is correct based on skill level and challenge difficulty
                    success_rate = {
                        'beginner': 0.3,
                        'intermediate': 0.5,
                        'advanced': 0.7,
                        'expert': 0.85
                    }[skill]
                    
                    # Reduce success rate for harder challenges
                    adjusted_success_rate = success_rate * (1.0 - (challenge.difficulty - 1) * 0.1)
                    
                    is_correct = random.random() < adjusted_success_rate
                    
                    if is_correct:
                        # Use correct flag
                        correct_flag = random.choice(challenge_flags)
                        flag_submitted = correct_flag.flag
                        solved_challenges.add((team, challenge))
                        
                        # Update team score
                        team.score += challenge.value
                        team.save()
                        
                    else:
                        # Use wrong flag
                        wrong_flags = [
                            'flag{wrong_answer}',
                            'flag{nice_try}',
                            'flag{not_quite}',
                            'flag{keep_trying}',
                            'ctf{wrong_format}',
                            f'flag{{{challenge.name.lower().replace(" ", "_")}_wrong}}',
                            'flag{almost_there}',
                            'flag{try_harder}',
                            'flag{404_not_found}',
                            'flag{permission_denied}'
                        ]
                        flag_submitted = random.choice(wrong_flags)
                    
                    submission = Submission.objects.create(
                        challenge=challenge,
                        user=user,
                        team=team,
                        flag_submitted=flag_submitted,
                        is_correct=is_correct,
                        submitted_at=submission_time
                    )
                    submissions.append(submission)
        
        # Create submissions for past event (all solved for variety)
        past_challenges = [c for c in challenges if c.event.status == 'finished']
        for challenge in past_challenges:
            for team in teams[:3]:  # Only first 3 teams participated in past event
                user = team.captain
                challenge_flags = challenge.flags.all()
                
                if challenge_flags:
                    correct_flag = random.choice(challenge_flags)
                    submission = Submission.objects.create(
                        challenge=challenge,
                        user=user,
                        team=team,
                        flag_submitted=correct_flag.flag,
                        is_correct=True,
                        submitted_at=challenge.event.start_time + timedelta(hours=random.randint(1, 48))
                    )
                    submissions.append(submission)
        
        self.stdout.write(f'Created {len(submissions)} submissions')
        return submissions
