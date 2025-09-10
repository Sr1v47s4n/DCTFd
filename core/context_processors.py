"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.conf import settings
from event.models import Event

def user_type(request):
    """
    Context processor to add user type information to the template context.
    """
    context = {
        'is_organizer': False,
        'is_superadmin': False,
        'is_regular_user': False,
    }

    if request.user.is_authenticated:
        # For the purpose of UI navigation
        # - Superadmins see admin interface
        # - Organizers see organizer interface
        # - Regular users see user interface
        if request.user.is_superuser:
            context['is_superadmin'] = True
        elif hasattr(request.user, 'is_organizer') and request.user.is_organizer:
            context['is_organizer'] = True
        else:
            context['is_regular_user'] = True

    return context


def event_info(request):
    """
    Context processor to add event information to the template context.
    """
    context = {
        "event_name": settings.EVENT_NAME,
        "event_logo_url": None,
        "event_favicon_url": None,
        "event_short_description": None,
        "event_description": None,
    }

    # Try to get the active event
    try:
        event = Event.objects.filter(status="active").first() or Event.objects.first()

        if event:
            context["event_name"] = event.name
            context["event_short_description"] = event.short_description
            context["event_description"] = event.description

            # Add logo and favicon URLs if available
            if hasattr(event, "settings") and event.settings:
                if event.settings.logo:
                    context["event_logo_url"] = event.settings.logo.url
                if event.settings.favicon:
                    context["event_favicon_url"] = event.settings.favicon.url

    except Exception:
        # Fallback to settings.EVENT_NAME if there's an error
        pass

    return context
