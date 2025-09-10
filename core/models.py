"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import uuid


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    """
    created_at = models.DateTimeField(
        _('created at'), 
        default=timezone.now,
        help_text=_('When this record was created')
    )
    updated_at = models.DateTimeField(
        _('updated at'), 
        auto_now=True,
        help_text=_('When this record was last updated')
    )

    class Meta:
        abstract = True


class Announcement(BaseModel):
    """
    Announcements made by organizers to participants during a CTF.
    """

    content = models.TextField(_("content"), help_text=_("The announcement message"))

    is_important = models.BooleanField(
        _("is important"),
        default=False,
        help_text=_("Whether this announcement should be highlighted as important"),
    )

    active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Whether this announcement is currently active"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("announcement")
        verbose_name_plural = _("announcements")

    def __str__(self):
        return f"Announcement ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class GlobalSettings(models.Model):
    """
    Site-wide settings for the platform.
    """
    # General settings
    site_name = models.CharField(
        _('site name'),
        max_length=100, 
        default='DCTFd',
        help_text=_('Name of the CTF platform')
    )
    
    site_description = models.TextField(
        _('site description'),
        blank=True,
        help_text=_('Brief description of the platform')
    )
    
    platform_version = models.CharField(
        _('platform version'),
        max_length=20, 
        default='1.0.0',
        help_text=_('Current version of the platform')
    )
    
    platform_logo = models.ImageField(
        _('platform logo'),
        upload_to='platform_assets/',
        blank=True,
        null=True,
        help_text=_('Logo for the platform')
    )
    
    platform_favicon = models.ImageField(
        _('platform favicon'),
        upload_to='platform_assets/',
        blank=True,
        null=True,
        help_text=_('Favicon for the platform')
    )
    
    # Theme settings
    default_theme = models.CharField(
        _('default theme'),
        max_length=50, 
        default='default',
        help_text=_('Default theme for the platform')
    )
    
    custom_css = models.TextField(
        _('custom CSS'),
        blank=True,
        help_text=_('Custom CSS for the entire platform')
    )
    
    custom_js = models.TextField(
        _('custom JavaScript'),
        blank=True,
        help_text=_('Custom JavaScript for the entire platform')
    )
    
    # Email settings
    email_from = models.EmailField(
        _('email from'),
        blank=True,
        help_text=_('Email address to send from')
    )
    
    email_contact = models.EmailField(
        _('contact email'),
        blank=True,
        help_text=_('Email address for contact inquiries')
    )
    
    # Feature flags
    allow_registration = models.BooleanField(
        _('allow registration'),
        default=True,
        help_text=_('Whether new users can register')
    )
    
    allow_team_creation = models.BooleanField(
        _('allow team creation'),
        default=True,
        help_text=_('Whether users can create teams')
    )
    
    allow_password_reset = models.BooleanField(
        _('allow password reset'),
        default=True,
        help_text=_('Whether users can reset passwords')
    )
    
    # User settings
    default_max_team_size = models.IntegerField(
        _('default maximum team size'),
        default=4,
        help_text=_('Default maximum team size for events')
    )
    
    default_user_role = models.CharField(
        _('default user role'),
        max_length=50, 
        default='user',
        help_text=_('Default role for new users')
    )
    
    require_email_verification = models.BooleanField(
        _('require email verification'),
        default=True,
        help_text=_('Whether email verification is required')
    )
    
    # Security settings
    enable_rate_limiting = models.BooleanField(
        _('enable rate limiting'),
        default=True,
        help_text=_('Whether to enable rate limiting')
    )
    
    max_login_attempts = models.IntegerField(
        _('maximum login attempts'),
        default=5,
        help_text=_('Maximum failed login attempts before lockout')
    )
    
    lockout_time = models.IntegerField(
        _('lockout time'),
        default=15,
        help_text=_('Minutes to lock account after too many failed attempts')
    )
    
    password_complexity_required = models.BooleanField(
        _('password complexity required'),
        default=True,
        help_text=_('Whether complex passwords are required')
    )
    
    # Maintenance settings
    maintenance_mode = models.BooleanField(
        _('maintenance mode'),
        default=False,
        help_text=_('Whether the site is in maintenance mode')
    )
    
    maintenance_message = models.TextField(
        _('maintenance message'),
        default='We are currently performing maintenance. Please check back later.',
        help_text=_('Message to display during maintenance')
    )
    
    # Analytics
    enable_analytics = models.BooleanField(
        _('enable analytics'),
        default=False,
        help_text=_('Whether to enable analytics tracking')
    )
    
    analytics_code = models.TextField(
        _('analytics code'),
        blank=True,
        help_text=_('Analytics tracking code')
    )
    
    last_updated = models.DateTimeField(
        _('last updated'),
        auto_now=True,
        help_text=_('When settings were last updated')
    )
    
    class Meta:
        verbose_name = _('global settings')
        verbose_name_plural = _('global settings')
    
    def __str__(self):
        return 'Global Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create the global settings object."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class Notification(BaseModel):
    """
    Model for storing user notifications.
    """
    NOTIFICATION_TYPES = [
        ('system', _('System')),
        ('event', _('Event')),
        ('team', _('Team')),
        ('challenge', _('Challenge')),
        ('achievement', _('Achievement')),
        ('message', _('Message')),
        ('announcement', _('Announcement'))
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_('User who received this notification')
    )
    
    title = models.CharField(
        _('title'),
        max_length=100,
        help_text=_('Title of the notification')
    )
    
    message = models.TextField(
        _('message'),
        help_text=_('Content of the notification')
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system',
        help_text=_('Type of notification')
    )
    
    is_read = models.BooleanField(
        _('is read'),
        default=False,
        help_text=_('Whether the notification has been read')
    )
    
    read_at = models.DateTimeField(
        _('read at'),
        blank=True,
        null=True,
        help_text=_('When the notification was read')
    )
    
    link = models.URLField(
        _('link'),
        blank=True,
        null=True,
        help_text=_('Optional link to direct user to')
    )
    
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='notifications',
        help_text=_('Associated event (if any)')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='notifications',
        help_text=_('Associated team (if any)')
    )
    
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='notifications',
        help_text=_('Associated challenge (if any)')
    )
    
    metadata = models.JSONField(
        _('metadata'),
        blank=True,
        null=True,
        help_text=_('Additional metadata for the notification')
    )
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
        return True


class AuditLog(BaseModel):
    """
    Model for tracking system activity for audit purposes.
    """
    ACTION_TYPES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('read', _('Read')),
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('register', _('Register')),
        ('reset_password', _('Reset Password')),
        ('admin', _('Admin Action')),
        ('error', _('Error')),
        ('security', _('Security Event'))
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='audit_logs',
        help_text=_('User who performed the action')
    )
    
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=ACTION_TYPES,
        help_text=_('Type of action performed')
    )
    
    model_name = models.CharField(
        _('model name'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Name of the model affected')
    )
    
    object_id = models.CharField(
        _('object ID'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('ID of the object affected')
    )
    
    object_repr = models.CharField(
        _('object representation'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('String representation of the object')
    )
    
    changes = models.JSONField(
        _('changes'),
        blank=True,
        null=True,
        help_text=_('Changes made to the object')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address from which the action was performed')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('User agent from which the action was performed')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        default='success',
        help_text=_('Status of the action')
    )
    
    message = models.TextField(
        _('message'),
        blank=True,
        null=True,
        help_text=_('Additional information about the action')
    )
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = f"{self.user.username}" if self.user else "Anonymous"
        return f"{user_info} - {self.get_action_display()} - {self.created_at}"


class Badge(BaseModel):
    """
    Model for badges that can be awarded to users.
    """
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Name of the badge')
    )
    
    description = models.TextField(
        _('description'),
        help_text=_('Description of the badge and how to earn it')
    )
    
    icon = models.ImageField(
        _('icon'),
        upload_to='badges/',
        help_text=_('Badge icon image')
    )
    
    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether the badge is currently active')
    )
    
    required_score = models.IntegerField(
        _('required score'),
        blank=True,
        null=True,
        help_text=_('Score required to earn this badge (if applicable)')
    )
    
    required_challenges = models.ManyToManyField(
        'challenges.Challenge',
        blank=True,
        related_name='required_for_badges',
        help_text=_('Challenges that must be completed to earn this badge')
    )
    
    hidden = models.BooleanField(
        _('hidden'),
        default=False,
        help_text=_('Whether the badge is hidden until earned')
    )
    
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='badges',
        help_text=_('Event this badge is associated with (if any)')
    )
    
    class Meta:
        verbose_name = _('badge')
        verbose_name_plural = _('badges')
    
    def __str__(self):
        return self.name


class UserBadge(BaseModel):
    """
    Model for tracking badges earned by users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
        help_text=_('User who earned the badge')
    )
    
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='awarded_to',
        help_text=_('Badge that was earned')
    )
    
    awarded_at = models.DateTimeField(
        _('awarded at'),
        default=timezone.now,
        help_text=_('When the badge was awarded')
    )
    
    reason = models.TextField(
        _('reason'),
        blank=True,
        null=True,
        help_text=_('Reason the badge was awarded')
    )
    
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='awarded_badges',
        help_text=_('Event during which the badge was earned (if any)')
    )
    
    class Meta:
        verbose_name = _('user badge')
        verbose_name_plural = _('user badges')
        unique_together = [['user', 'badge', 'event']]
        ordering = ['-awarded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class Page(BaseModel):
    """
    Model for static pages on the platform.
    """
    title = models.CharField(
        _('title'),
        max_length=100,
        help_text=_('Page title')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=120,
        unique=True,
        help_text=_('URL-friendly name for the page')
    )
    
    content = models.TextField(
        _('content'),
        help_text=_('Page content (supports Markdown)')
    )
    
    is_published = models.BooleanField(
        _('is published'),
        default=True,
        help_text=_('Whether the page is visible')
    )
    
    auth_required = models.BooleanField(
        _('authentication required'),
        default=False,
        help_text=_('Whether authentication is required to view')
    )
    
    show_in_footer = models.BooleanField(
        _('show in footer'),
        default=False,
        help_text=_('Whether to show in the footer navigation')
    )
    
    show_in_header = models.BooleanField(
        _('show in header'),
        default=False,
        help_text=_('Whether to show in the header navigation')
    )
    
    order = models.IntegerField(
        _('order'),
        default=0,
        help_text=_('Order in navigation')
    )
    
    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class File(BaseModel):
    """
    Model for storing files related to challenges, events, etc.
    """
    name = models.CharField(
        _('name'),
        max_length=255,
        help_text=_('Name of the file')
    )
    
    file = models.FileField(
        _('file'),
        upload_to='files/%Y/%m/',
        help_text=_('The actual file')
    )
    
    size = models.BigIntegerField(
        _('size'),
        help_text=_('Size of the file in bytes')
    )
    
    mimetype = models.CharField(
        _('MIME type'),
        max_length=100,
        help_text=_('MIME type of the file')
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Description of the file')
    )
    
    # Optional relations to link this file to different entities
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='core_files',
        help_text=_('Challenge this file belongs to (if any)')
    )
    
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='files',
        help_text=_('Event this file belongs to (if any)')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='files',
        help_text=_('Team this file belongs to (if any)')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='uploaded_files',
        help_text=_('User who uploaded this file')
    )
    
    uuid = models.UUIDField(
        _('UUID'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Unique identifier for the file')
    )
    
    is_public = models.BooleanField(
        _('is public'),
        default=False,
        help_text=_('Whether the file is publicly accessible')
    )
    
    download_count = models.IntegerField(
        _('download count'),
        default=0,
        help_text=_('Number of times the file has been downloaded')
    )
    
    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def increment_download_count(self):
        """Increment the download count for this file."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
        return self.download_count


class ActivityLog(BaseModel):
    """
    Model for tracking user activity on the platform.
    """
    ACTIVITY_TYPES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('register', _('Register')),
        ('profile_update', _('Profile Update')),
        ('password_change', _('Password Change')),
        ('password_reset', _('Password Reset')),
        ('team_create', _('Team Create')),
        ('team_join', _('Team Join')),
        ('team_leave', _('Team Leave')),
        ('challenge_view', _('Challenge View')),
        ('challenge_solve', _('Challenge Solve')),
        ('flag_submit', _('Flag Submit')),
        ('hint_unlock', _('Hint Unlock')),
        ('event_register', _('Event Register')),
        ('file_download', _('File Download')),
        ('other', _('Other'))
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text=_('User who performed the activity')
    )
    
    activity_type = models.CharField(
        _('activity type'),
        max_length=20,
        choices=ACTIVITY_TYPES,
        help_text=_('Type of activity')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address from which the activity was performed')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('User agent from which the activity was performed')
    )
    
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='activity_logs',
        help_text=_('Event associated with this activity (if any)')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='activity_logs',
        help_text=_('Team associated with this activity (if any)')
    )
    
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='activity_logs',
        help_text=_('Challenge associated with this activity (if any)')
    )
    
    metadata = models.JSONField(
        _('metadata'),
        blank=True,
        null=True,
        help_text=_('Additional metadata about the activity')
    )
    
    class Meta:
        verbose_name = _('activity log')
        verbose_name_plural = _('activity logs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.created_at}"
