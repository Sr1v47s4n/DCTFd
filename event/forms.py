"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Event, EventSettings
from django.utils import timezone
from django.core.exceptions import ValidationError
import pytz

User = get_user_model()

class EventSetupForm(forms.ModelForm):
    """Form for initial event setup"""
    
    # Root admin user creation fields
    admin_username = forms.CharField(
        label=_('Admin Username'),
        max_length=150,
        required=True,
        help_text=_('Username for the root administrator'),
        widget=forms.TextInput(attrs={'placeholder': 'admin'})
    )
    
    admin_email = forms.EmailField(
        label=_('Admin Email'),
        required=True,
        help_text=_('Email address for the root administrator'),
        widget=forms.EmailInput(attrs={'placeholder': 'admin@example.com'})
    )
    
    admin_password = forms.CharField(
        label=_('Admin Password'),
        required=True,
        help_text=_('Password for the root administrator'),
        widget=forms.PasswordInput()
    )
    
    admin_password_confirm = forms.CharField(
        label=_('Confirm Admin Password'),
        required=True,
        help_text=_('Confirm password for the root administrator'),
        widget=forms.PasswordInput()
    )
    
    # Time settings with timezone support
    timezone = forms.ChoiceField(
        label=_('Event Timezone'),
        required=True,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial='UTC',
        help_text=_('Timezone for event times')
    )
    
    # Theme customization
    theme = forms.ChoiceField(
        label=_('Theme'),
        required=True,
        choices=[
            ('default', _('Default')),
            ('dark', _('Dark')),
            ('light', _('Light')),
            ('hacker', _('Hacker')),
            ('cyberpunk', _('Cyberpunk')),
        ],
        initial='default',
        help_text=_('Visual theme for the event')
    )
    
    # Color scheme
    primary_color = forms.CharField(
        label=_('Primary Color'),
        required=False,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#3498db'}),
        help_text=_('Primary brand color')
    )
    
    secondary_color = forms.CharField(
        label=_('Secondary Color'),
        required=False,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#2ecc71'}),
        help_text=_('Secondary brand color')
    )
    
    accent_color = forms.CharField(
        label=_('Accent Color'),
        required=False,
        widget=forms.TextInput(attrs={'type': 'color', 'value': '#e74c3c'}),
        help_text=_('Accent color for highlights')
    )
    
    # Event format
    event_format = forms.ChoiceField(
        label=_('Event Format'),
        required=True,
        choices=[
            ('team', _('Team-based')),
            ('individual', _('Individual')),
            ('hybrid', _('Hybrid (Both team and individual)'))
        ],
        initial='team',
        help_text=_('Format for participation')
    )
    
    # Event assets
    logo = forms.ImageField(
        label=_('Event Logo'),
        required=False,
        help_text=_('Logo displayed throughout the event (Recommended size: 512x512px)')
    )
    
    banner = forms.ImageField(
        label=_('Event Banner'),
        required=False,
        help_text=_('Banner displayed on event header (Recommended size: 1920x400px)')
    )
    
    favicon = forms.ImageField(
        label=_('Favicon'),
        required=False,
        help_text=_('Icon displayed in browser tabs (Recommended size: 32x32px)')
    )
    
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'short_description',
            'start_time', 'end_time', 
            'registration_start', 'registration_end',
            'access', 'max_team_size', 'min_team_size',
            'allow_individual_participants'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Password confirmation check
        password = cleaned_data.get('admin_password')
        confirm_password = cleaned_data.get('admin_password_confirm')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('admin_password_confirm', _('Passwords do not match'))
        
        # Time validation
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        registration_start = cleaned_data.get('registration_start')
        registration_end = cleaned_data.get('registration_end')
        
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', _('End time must be after start time'))
        
        if registration_start and registration_end and registration_start >= registration_end:
            self.add_error('registration_end', _('Registration end must be after registration start'))
        
        if registration_end and start_time and registration_end > start_time:
            self.add_error('registration_end', _('Registration should end before the event starts'))
        
        # Team size validation
        min_team_size = cleaned_data.get('min_team_size')
        max_team_size = cleaned_data.get('max_team_size')
        
        if min_team_size and max_team_size and min_team_size > max_team_size:
            self.add_error('min_team_size', _('Minimum team size cannot be greater than maximum team size'))
        
        return cleaned_data

class EventSettingsForm(forms.ModelForm):
    """Form for event settings during setup"""
    
    class Meta:
        model = EventSettings
        fields = [
            'allow_zero_point_challenges', 'use_dynamic_scoring',
            'require_email_verification', 'auto_approve_participants',
            'allow_team_creation', 'allow_team_joining',
            'show_challenges_before_start', 'allow_challenge_feedback',
            'enable_team_communication', 'enable_hints',
            'theme', 'custom_css', 'custom_js',
            'submission_cooldown', 'max_submissions_per_minute'
        ]
        widgets = {
            'custom_css': forms.Textarea(attrs={'rows': 5, 'class': 'code-editor'}),
            'custom_js': forms.Textarea(attrs={'rows': 5, 'class': 'code-editor'}),
        }
