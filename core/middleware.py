"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError
import traceback
import logging
import time
from django.utils import timezone

logger = logging.getLogger("dctfd")

class DevelopmentSetupMiddleware:
    """
    Middleware to automatically setup development environment when DEV_MODE is enabled.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.setup_completed = False
        self.setup_attempted = False

    def __call__(self, request):
        # Only do this once per server start and only in development mode
        if settings.DEV_MODE and not self.setup_completed and not self.setup_attempted:
            self.setup_attempted = True

            # Check if database is ready
            db_conn = connections['default']
            try:
                c = db_conn.cursor()
                c.execute('SELECT 1')
                # If we get here, the database is ready

                try:
                    # Call the setup_dev command
                    call_command('setup_dev')
                    self.setup_completed = True
                except Exception as e:
                    # Log the error but continue - don't crash the entire application
                    print(f"Error during development setup: {str(e)}")
                    traceback.print_exc()
            except OperationalError:
                # Database is not ready yet, we'll try again on the next request
                pass

        response = self.get_response(request)
        return response


class ActivityLogMiddleware:
    """
    Middleware to log user activities including login, page views, and operations.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        # Log activity after the view has been processed
        self.log_activity(request, response, duration)

        return response

    def log_activity(self, request, response, duration):
        """Log user activity with relevant details."""
        # Don't log static files, media, or favicon requests
        if any(
            path in request.path for path in ["/static/", "/media/", "/favicon.ico"]
        ):
            return

        # Get basic request info
        method = request.method
        path = request.path
        status_code = response.status_code

        # Get user info if authenticated
        user_info = "Anonymous"
        if request.user.is_authenticated:
            user_info = f"{request.user.username} (ID: {request.user.id})"
            if hasattr(request.user, "team") and request.user.team:
                user_info += f", Team: {request.user.team.name}"

        # Get IP address
        ip_address = self.get_client_ip(request)

        # Log the activity
        log_data = {
            "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_info,
            "method": method,
            "path": path,
            "status_code": status_code,
            "ip_address": ip_address,
            "duration": f"{duration:.4f}s",
        }

        # Determine log level based on status code
        if 200 <= status_code < 300:
            logger.info(f"[USER] {user_info} - {method} {path} - {status_code}")
        elif 300 <= status_code < 400:
            logger.info(f"[REDIRECT] {user_info} - {method} {path} - {status_code}")
        elif 400 <= status_code < 500:
            logger.warning(
                f"[CLIENT ERROR] {user_info} - {method} {path} - {status_code}"
            )
        else:
            logger.error(
                f"[SERVER ERROR] {user_info} - {method} {path} - {status_code}"
            )

    def get_client_ip(self, request):
        """Get the client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "Unknown")
