"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Load environment variables from .env file if it exists
    try:
        import dotenv

        env_file = os.path.join(Path(__file__).resolve().parent, ".env")
        if os.path.exists(env_file):
            dotenv.load_dotenv(env_file)
    except ImportError:
        pass

    # Use the new settings structure
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DCTFd.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
