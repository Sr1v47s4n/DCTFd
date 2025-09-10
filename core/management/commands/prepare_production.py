"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
import os
import sys
import secrets
import string
import subprocess
import django
from pathlib import Path

User = get_user_model()

class Command(BaseCommand):
    help = 'Prepare the DCTFd instance for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--generate-env',
            action='store_true',
            help='Generate a .env file with secure values',
        )
        parser.add_argument(
            '--check-security',
            action='store_true',
            help='Run Django deployment checks',
        )
        parser.add_argument(
            '--collect-static',
            action='store_true',
            help='Collect static files',
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account if none exists',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all preparation steps',
        )

    def handle(self, *args, **options):
        if options['all']:
            options['generate_env'] = True
            options['check_security'] = True
            options['collect_static'] = True
            options['create_superuser'] = True

        if options['generate_env']:
            self.generate_env_file()

        if options['check_security']:
            self.check_security()

        if options['collect_static']:
            self.collect_static()

        if options['create_superuser']:
            self.create_superuser()

        self.stdout.write(self.style.SUCCESS('Production preparation completed!'))

        # Print summary of what was done
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Review the .env file and update values as needed')
        self.stdout.write("2. Set DJANGO_ENVIRONMENT=production")
        self.stdout.write('3. Run migrations: python manage.py migrate')
        self.stdout.write('4. Deploy according to the PRODUCTION_DEPLOYMENT.md guide')

    def generate_env_file(self):
        """Generate a .env file with secure values"""
        self.stdout.write('Generating .env file...')

        env_path = Path(settings.BASE_DIR) / '.env'

        # Check if .env already exists
        if env_path.exists():
            overwrite = input('.env file already exists. Overwrite? (y/n): ')
            if overwrite.lower() != 'y':
                self.stdout.write(self.style.WARNING('Skipping .env generation'))
                return

        # Generate a secure secret key
        alphabet = string.ascii_letters + string.digits + string.punctuation
        secret_key = ''.join(secrets.choice(alphabet) for _ in range(50))

        # Create .env content
        env_content = f"""# DCTFd Production Environment Variables
# Generated on {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
DJANGO_ENVIRONMENT=production

# Database Settings
DB_NAME=dctfd_db
DB_USER=dctfd_user
DB_PASSWORD=dctfd_postgres_password
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgres://dctfd_user:dctfd_postgres_password@db:5432/dctfd_db

# Redis Cache Settings
REDIS_URL=redis://127.0.0.1:6379/1

# Environment Settings
DJANGO_ENVIRONMENT=production

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
"""

        # Write to .env file
        with open(env_path, 'w') as env_file:
            env_file.write(env_content)

        self.stdout.write(self.style.SUCCESS('.env file generated successfully'))
        self.stdout.write(self.style.WARNING('IMPORTANT: Update the placeholder values in the .env file with your actual settings'))

    def check_security(self):
        """Run Django deployment checks"""
        self.stdout.write('Running security checks...')

        # Set to production settings temporarily for the check
        original_environment = os.environ.get("DJANGO_ENVIRONMENT")
        os.environ["DJANGO_ENVIRONMENT"] = "production"

        try:
            # Run the check command
            subprocess.run([sys.executable, 'manage.py', 'check', '--deploy'], check=True)
            self.stdout.write(self.style.SUCCESS('Security checks completed'))
        except subprocess.CalledProcessError:
            self.stdout.write(self.style.ERROR('Security checks failed. Please fix the issues above.'))
        finally:
            # Restore original settings
            if original_environment:
                os.environ["DJANGO_ENVIRONMENT"] = original_environment
            else:
                os.environ.pop("DJANGO_ENVIRONMENT", None)

    def collect_static(self):
        """Collect static files"""
        self.stdout.write('Collecting static files...')

        try:
            # Run collectstatic command
            subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput'], check=True)
            self.stdout.write(self.style.SUCCESS('Static files collected successfully'))
        except subprocess.CalledProcessError:
            self.stdout.write(self.style.ERROR('Failed to collect static files'))

    def create_superuser(self):
        """Create a superuser if none exists"""
        self.stdout.write('Checking for existing superusers...')

        # Check if any superuser exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
            return

        self.stdout.write('No superuser found. Creating new superuser...')

        try:
            # Create superuser interactively
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=True)
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        except subprocess.CalledProcessError:
            self.stdout.write(self.style.ERROR('Failed to create superuser'))
