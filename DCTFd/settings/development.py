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
EVENT_NAME = os.environ.get("EVENT_NAME", "DCTFd")

# Update SITE_NAME to use EVENT_NAME
SITE_NAME = EVENT_NAME

# In development, allow all hosts
ALLOWED_HOSTS = ["*"]

# Database - use PostgreSQL from Docker for both environments
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Use dj_database_url to parse the DATABASE_URL
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    # Default to SQLite for development if DATABASE_URL is not set
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# For development, use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
