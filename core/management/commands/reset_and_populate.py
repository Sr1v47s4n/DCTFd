"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

"""
Management command to reset the database and populate with fresh sample data
"""
import os
import subprocess
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

class Command(BaseCommand):
    help = 'Reset database and populate with comprehensive sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations (use if migrations are already applied)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('This will delete all existing data and reset the database!'))
        
        # Confirm action
        confirm = input('Are you sure you want to continue? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return

        self.stdout.write(self.style.SUCCESS('Starting database reset...'))

        # Delete database file if using SQLite
        if 'sqlite' in settings.DATABASES['default']['ENGINE']:
            db_path = settings.DATABASES['default']['NAME']
            if os.path.exists(db_path):
                os.remove(db_path)
                self.stdout.write(f'Deleted SQLite database: {db_path}')

        # Run migrations unless skipped
        if not options['skip_migrations']:
            self.stdout.write(self.style.SUCCESS('Running migrations...'))
            call_command('makemigrations')
            call_command('migrate')

        # Populate with sample data
        self.stdout.write(self.style.SUCCESS('Populating database with sample data...'))
        call_command('populate_sample_data')

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Database reset complete!\n\n'
                'Sample Login Credentials:\n'
                '========================\n'
                'Super Admin:\n'
                '  Username: admin\n'
                '  Password: admin123\n\n'
                'Organizer Accounts:\n'
                '  Username: organizer1 | Password: organizer123\n'
                '  Username: organizer2 | Password: organizer123\n'
                '  Username: organizer3 | Password: organizer123\n\n'
                'Sample Users:\n'
                '  Username: alice_hacker | Password: user123\n'
                '  Username: bob_security | Password: user123\n'
                '  Username: charlie_crypto | Password: user123\n'
                '  (and 9 more users with password: user123)\n\n'
                'Sample Teams:\n'
                '  - CyberGuardians (Captain: alice_hacker)\n'
                '  - SecurityNinjas (Captain: diana_detective)\n'
                '  - DigitalDetectives (Captain: grace_pwn)\n'
                '  - PwnMasters (Captain: jack_misc)\n\n'
                'Events:\n'
                '  - CyberSec Championship 2025 (Active)\n'
                '  - Spring CTF 2025 (Past)\n'
                '  - Advanced Hacking Contest 2025 (Future)\n\n'
                'Features Included:\n'
                '  ✓ Custom Fields for Users and Teams\n'
                '  ✓ 12 Sample Challenges across 8 categories\n'
                '  ✓ Hints for selected challenges\n'
                '  ✓ Sample submissions (correct and incorrect)\n'
                '  ✓ Multiple events with different statuses\n\n'
                'You can now test all features of DCTFd!\n'
            )
        )
