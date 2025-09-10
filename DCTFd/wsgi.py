"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

"""
WSGI config for DCTFd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import dotenv
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Load environment variables from .env file
env_file = os.path.join(Path(__file__).resolve().parent.parent, ".env")
if os.path.exists(env_file):
    dotenv.load_dotenv(env_file)

# Set default settings module to use the new structure
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCTFd.settings")

application = get_wsgi_application()
