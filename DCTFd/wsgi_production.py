"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

#!/usr/bin/env python
"""
WSGI config for DCTFd production deployment.
"""

import os
import sys
from pathlib import Path
import dotenv

# Add the project directory to the sys.path
path = str(Path(__file__).resolve().parent.parent)
if path not in sys.path:
    sys.path.append(path)

# Load environment variables from .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Set the Django settings module and environment
os.environ.setdefault("DJANGO_ENVIRONMENT", "production")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCTFd.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
