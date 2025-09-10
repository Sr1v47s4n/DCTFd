"""
Development settings for DCTFd project.

DCTFd - A Capture The Flag platform built with Django
Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import os
import dj_database_url
from .base import *  # Import base settings

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-oiwul3d$hyc=d=z_%04=fj=$n46!d!x$bj*ns+k#)g^qhicbi@"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development mode flag - set to True for automatic configuration
DEV_MODE = True

# Default CTF Event Name
EVENT_NAME = os.environ.get("EVENT_NAME", "Section 13(September Edition)")

# Update SITE_NAME to use EVENT_NAME
SITE_NAME = EVENT_NAME

# In development, allow all hosts
ALLOWED_HOSTS = ["*"]

# Database - use PostgreSQL from Docker for both environments
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            'DATABASE_URL', 
            f"postgres://{os.environ.get('DB_USER', 'dctfd_user')}:{os.environ.get('DB_PASSWORD', 'dctfd_postgres_password')}@{os.environ.get('DB_HOST', 'db')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'dctfd_db')}"
        ),
        conn_max_age=600
    )
}

# For development, use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'