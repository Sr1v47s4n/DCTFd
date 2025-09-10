"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import pytz
import os
import json

from .models import Event, EventSettings
from .forms import EventSetupForm, EventSettingsForm
from core.models import GlobalSettings

User = get_user_model()

def event_setup(request):
    """
    View for the initial event setup page.
    Includes form for configuring:
    - Event details
    - Root admin user
    - Theme/appearance
    - Registration settings
    """
    # Check if any events already exist
    if Event.objects.exists():
        messages.warning(request, _('Event setup has already been completed. Please use the admin panel for further configuration.'))
        return redirect('admin:index')

    # Initialize forms
    form = EventSetupForm(request.POST or None, request.FILES or None)
    settings_form = EventSettingsForm(request.POST or None)

    if request.method == 'POST':
        form_valid = form.is_valid()
        settings_form_valid = settings_form.is_valid()

        # Debug logging
        if not form_valid:
            print("Form errors:", form.errors)
            messages.error(
                request,
                _(
                    "There are errors in the event setup form. Please check the form and try again."
                ),
            )

        if not settings_form_valid:
            print("Settings form errors:", settings_form.errors)
            messages.error(
                request,
                _(
                    "There are errors in the event settings form. Please check the form and try again."
                ),
            )

        if form_valid and settings_form_valid:
            # Save to session for confirmation page
            request.session['event_setup_data'] = {
                'form_data': {k: str(v) for k, v in form.cleaned_data.items() if k != 'logo' and k != 'banner' and k != 'favicon'},
                'settings_data': {k: str(v) for k, v in settings_form.cleaned_data.items()},
            }

            # Handle file uploads separately
            if 'logo' in request.FILES:
                # Save temporarily and store the path
                logo_path = os.path.join('temp', request.FILES['logo'].name)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'), exist_ok=True)
                with open(os.path.join(settings.MEDIA_ROOT, logo_path), 'wb+') as destination:
                    for chunk in request.FILES['logo'].chunks():
                        destination.write(chunk)
                request.session['event_setup_data']['logo_path'] = logo_path

            if 'banner' in request.FILES:
                banner_path = os.path.join('temp', request.FILES['banner'].name)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'), exist_ok=True)
                with open(os.path.join(settings.MEDIA_ROOT, banner_path), 'wb+') as destination:
                    for chunk in request.FILES['banner'].chunks():
                        destination.write(chunk)
                request.session['event_setup_data']['banner_path'] = banner_path

            if 'favicon' in request.FILES:
                favicon_path = os.path.join('temp', request.FILES['favicon'].name)
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp'), exist_ok=True)
                with open(os.path.join(settings.MEDIA_ROOT, favicon_path), 'wb+') as destination:
                    for chunk in request.FILES['favicon'].chunks():
                        destination.write(chunk)
                request.session['event_setup_data']['favicon_path'] = favicon_path

            # Redirect to confirmation/summary page
            return redirect('event:save')

    context = {
        'form': form,
        'settings_form': settings_form,
        'timezones': pytz.common_timezones,
    }

    return render(request, 'event/setup.html', context)

def event_save(request):
    """
    View for saving the event setup data and creating the initial resources.
    """
    # Check if any events already exist
    if Event.objects.exists():
        messages.warning(request, _('Event setup has already been completed. Please use the admin panel for further configuration.'))
        return redirect('admin:index')
    
    # Check if we have setup data in the session
    if 'event_setup_data' not in request.session:
        messages.error(request, _('No setup data found. Please fill out the setup form.'))
        return redirect('event:setup')
    
    if request.method == 'POST':
        try:
            setup_data = request.session['event_setup_data']
            form_data = setup_data.get('form_data', {})
            settings_data = setup_data.get('settings_data', {})
            
            # Create the admin user first
            admin_user = User.objects.create_superuser(
                username=form_data.get('admin_username'),
                email=form_data.get('admin_email'),
                password=form_data.get('admin_password'),
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True,
                type='admin'
            )
            
            # Convert string dates back to datetime objects
            date_fields = ['start_time', 'end_time', 'registration_start', 'registration_end']
            for field in date_fields:
                if field in form_data:
                    # Handle the datetime format from the form
                    form_data[field] = timezone.datetime.fromisoformat(form_data[field])
            
            # Create the event
            event_data = {k: v for k, v in form_data.items() if k not in [
                'admin_username', 'admin_email', 'admin_password', 'admin_password_confirm',
                'timezone', 'theme', 'primary_color', 'secondary_color', 'accent_color',
                'event_format', 'logo', 'banner', 'favicon'
            ]}
            
            event = Event.objects.create(
                **event_data,
                created_by=admin_user,
                status='planning'
            )
            
            # Handle event format setting
            event_format = form_data.get('event_format')
            if event_format == 'individual':
                event.allow_individual_participants = True
                event.min_team_size = 1
                event.max_team_size = 1
            elif event_format == 'team':
                event.allow_individual_participants = False
            # For 'hybrid', the default settings from the form will apply
            
            event.save()
            
            # Create event settings
            event_settings = EventSettings.objects.create(
                event=event,
                theme=form_data.get('theme', 'default'),
                **{k: v for k, v in settings_data.items() if k not in ['theme']}
            )
            
            # Move and assign any uploaded files
            if 'logo_path' in setup_data:
                temp_path = os.path.join(settings.MEDIA_ROOT, setup_data['logo_path'])
                final_path = os.path.join('event_logos', os.path.basename(temp_path))
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'event_logos'), exist_ok=True)
                os.rename(temp_path, os.path.join(settings.MEDIA_ROOT, final_path))
                event.logo = final_path
            
            if 'banner_path' in setup_data:
                temp_path = os.path.join(settings.MEDIA_ROOT, setup_data['banner_path'])
                final_path = os.path.join('event_banners', os.path.basename(temp_path))
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'event_banners'), exist_ok=True)
                os.rename(temp_path, os.path.join(settings.MEDIA_ROOT, final_path))
                event.banner = final_path
            
            if 'favicon_path' in setup_data:
                temp_path = os.path.join(settings.MEDIA_ROOT, setup_data['favicon_path'])
                final_path = os.path.join('platform_assets', os.path.basename(temp_path))
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'platform_assets'), exist_ok=True)
                os.rename(temp_path, os.path.join(settings.MEDIA_ROOT, final_path))
                
                # Update global settings with favicon
                global_settings = GlobalSettings.get_settings()
                global_settings.platform_favicon = final_path
                global_settings.save()
            
            # Update global settings
            global_settings = GlobalSettings.get_settings()
            global_settings.site_name = event.name
            global_settings.site_description = event.short_description
            global_settings.default_theme = form_data.get('theme', 'default')
            
            # Save custom colors as custom CSS
            custom_css = ""
            if 'primary_color' in form_data:
                custom_css += f":root {{ --primary-color: {form_data['primary_color']}; }}\n"
            if 'secondary_color' in form_data:
                custom_css += f":root {{ --secondary-color: {form_data['secondary_color']}; }}\n"
            if 'accent_color' in form_data:
                custom_css += f":root {{ --accent-color: {form_data['accent_color']}; }}\n"
            
            if custom_css:
                global_settings.custom_css = custom_css
            
            global_settings.save()
            
            # Save the final event after all updates
            event.save()
            
            # Clear session data
            if 'event_setup_data' in request.session:
                del request.session['event_setup_data']
            
            messages.success(request, _('Event setup completed successfully! You can now log in as the administrator.'))
            return redirect('admin:index')
            
        except Exception as e:
            messages.error(request, _('Error during setup: ') + str(e))
            return redirect('event:setup')
    
    # Display confirmation page
    setup_data = request.session['event_setup_data']
    form_data = setup_data.get('form_data', {})
    settings_data = setup_data.get('settings_data', {})
    
    # Determine if we have file uploads
    has_logo = 'logo_path' in setup_data
    has_banner = 'banner_path' in setup_data
    has_favicon = 'favicon_path' in setup_data
    
    context = {
        'form_data': form_data,
        'settings_data': settings_data,
        'has_logo': has_logo,
        'has_banner': has_banner,
        'has_favicon': has_favicon,
    }
    
    return render(request, 'event/save.html', context)
