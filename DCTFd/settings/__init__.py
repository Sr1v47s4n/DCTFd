"""
Settings initialization for DCTFd project.

This module determines which settings file to load based on the DJANGO_SETTINGS_MODULE
environment variable or defaults to development settings.

DCTFd - A Capture The Flag platform built with Django
Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import os

# Determine which settings to load based on environment variable
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *