"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import os
import re
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import dotenv


class Command(BaseCommand):
    help = "Toggle development mode on or off and create a .env file"

    def add_arguments(self, parser):
        parser.add_argument(
            "mode", type=str, help='Turn development mode "on" or "off"'
        )

    def handle(self, *args, **options):
        mode = options["mode"].lower()

        if mode not in ["on", "off"]:
            raise CommandError('Mode must be either "on" or "off"')

        # Path to .env file
        env_file = os.path.join(settings.BASE_DIR, ".env")

        # Create or update the .env file
        self._update_env_file(env_file, mode)

        # If we're turning dev mode on, run the setup_dev command
        if mode == "on":
            # Set environment variable for the current process
            os.environ["DEV_MODE"] = "True"
            call_command("setup_dev")
            # Also set up default avatars
            call_command("setup_avatars")
        else:
            # Set environment variable for the current process
            os.environ["DEV_MODE"] = "False"

        self.stdout.write(self.style.SUCCESS(f"Development mode turned {mode}"))
        self.stdout.write(self.style.SUCCESS(f"Environment file updated at {env_file}"))
        self.stdout.write(
            self.style.WARNING("Restart your server for changes to take effect")
        )

    def _update_env_file(self, env_file, mode):
        env_vars = {}

        # Read existing .env file if it exists
        if os.path.exists(env_file):
            dotenv_file = dotenv.find_dotenv(env_file)
            if dotenv_file:
                dotenv.load_dotenv(dotenv_file)

                # Extract existing variables
                with open(env_file, "r") as f:
                    for line in f:
                        if "=" in line and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            env_vars[key] = value

        # Update DEV_MODE value
        env_vars["DEV_MODE"] = "True" if mode == "on" else "False"

        # Set sensible defaults for development mode
        if mode == "on":
            env_vars["DEBUG"] = "True"
            env_vars["SECRET_KEY"] = env_vars.get(
                "SECRET_KEY", "django-insecure-dev-mode-secret-key"
            )
            env_vars["ALLOWED_HOSTS"] = env_vars.get(
                "ALLOWED_HOSTS", "localhost,127.0.0.1"
            )

        # Write to .env file
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
