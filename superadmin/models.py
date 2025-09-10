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
from django.core.validators import MinValueValidator, MaxValueValidator


class PlatformConfiguration(models.Model):
    """
    Model for storing platform-wide configurations that can be modified by superadmins.
    Implements a singleton pattern to ensure only one instance exists.
    """
    # Site Information
    site_name = models.CharField(
        _('site name'),
        max_length=128,
        default='DCTFd',
        help_text=_('Name of the CTF platform')
    )
    
    site_description = models.TextField(
        _('site description'),
        default='CTF Platform',
        help_text=_('Brief description of the platform')
    )
    
    platform_logo = models.ImageField(
        _('platform logo'),
        upload_to='platform/',
        null=True,
        blank=True,
        help_text=_('Logo to display on the platform')
    )
    
    favicon = models.ImageField(
        _('favicon'),
        upload_to='platform/',
        null=True,
        blank=True,
        help_text=_('Favicon for the website')
    )
    
    # Contact Information
    admin_email = models.EmailField(
        _('admin email'),
        default='admin@example.com',
        help_text=_('Email address for administrative contact')
    )
    
    support_email = models.EmailField(
        _('support email'),
        default='support@example.com',
        help_text=_('Email address for support inquiries')
    )
    
    # Social Media
    twitter_handle = models.CharField(
        _('twitter handle'),
        max_length=15,
        blank=True,
        null=True,
        help_text=_('Twitter handle without the @ symbol')
    )
    
    facebook_url = models.URLField(
        _('facebook URL'),
        blank=True,
        null=True,
        help_text=_('Facebook page URL')
    )
    
    discord_invite = models.CharField(
        _('discord invite'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Discord invite code')
    )
    
    github_url = models.URLField(
        _('github URL'),
        blank=True,
        null=True,
        help_text=_('GitHub repository URL')
    )
    
    # Global Feature Toggles
    enable_registration = models.BooleanField(
        _('enable registration'),
        default=True,
        help_text=_('Allow new users to register')
    )
    
    require_email_verification = models.BooleanField(
        _('require email verification'),
        default=True,
        help_text=_('Require email verification for new accounts')
    )
    
    enable_team_creation = models.BooleanField(
        _('enable team creation'),
        default=True,
        help_text=_('Allow users to create teams')
    )
    
    enable_public_scoreboard = models.BooleanField(
        _('enable public scoreboard'),
        default=True,
        help_text=_('Make the scoreboard visible to non-participants')
    )
    
    # Team Configurations
    max_team_size = models.IntegerField(
        _('maximum team size'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_('Maximum members allowed in a team (platform-wide default)')
    )
    
    # Rate Limiting
    max_login_attempts = models.IntegerField(
        _('maximum login attempts'),
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_('Maximum failed login attempts before temporary lockout')
    )
    
    max_submissions_per_minute = models.IntegerField(
        _('maximum submissions per minute'),
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text=_('Maximum flag submission attempts per minute')
    )
    
    # Maintenance
    maintenance_mode = models.BooleanField(
        _('maintenance mode'),
        default=False,
        help_text=_('Put the platform in maintenance mode (only admins can access)')
    )
    
    maintenance_message = models.TextField(
        _('maintenance message'),
        default='The platform is currently undergoing maintenance. Please check back later.',
        help_text=_('Message displayed during maintenance mode')
    )
    
    # Versioning
    platform_version = models.CharField(
        _('platform version'),
        max_length=20,
        default='1.0.0',
        help_text=_('Current version of the platform')
    )
    
    # Analytics
    enable_analytics = models.BooleanField(
        _('enable analytics'),
        default=False,
        help_text=_('Enable analytics tracking')
    )
    
    analytics_code = models.TextField(
        _('analytics code'),
        blank=True,
        null=True,
        help_text=_('Analytics tracking code (e.g., Google Analytics)')
    )
    
    # Terms and Policies
    terms_of_service = models.TextField(
        _('terms of service'),
        blank=True,
        null=True,
        help_text=_('Terms of service text')
    )
    
    privacy_policy = models.TextField(
        _('privacy policy'),
        blank=True,
        null=True,
        help_text=_('Privacy policy text')
    )
    
    # Record keeping
    last_updated = models.DateTimeField(
        _('last updated'),
        auto_now=True,
        help_text=_('When the configuration was last updated')
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='platform_config_updates',
        help_text=_('User who last updated the configuration')
    )
    
    class Meta:
        verbose_name = _('platform configuration')
        verbose_name_plural = _('platform configurations')
    
    def __str__(self):
        return f"Platform Configuration ({self.site_name})"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance of this model exists."""
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get the platform configuration, creating it if it doesn't exist."""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class SystemLog(models.Model):
    """
    Model for tracking system-level events and actions.
    """
    LOG_LEVEL_CHOICES = [
        ('debug', _('Debug')),
        ('info', _('Info')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('critical', _('Critical'))
    ]
    
    LOG_CATEGORY_CHOICES = [
        ('security', _('Security')),
        ('user', _('User Management')),
        ('team', _('Team Management')),
        ('challenge', _('Challenge Management')),
        ('event', _('Event Management')),
        ('system', _('System Management')),
        ('performance', _('Performance')),
        ('other', _('Other'))
    ]
    
    timestamp = models.DateTimeField(
        _('timestamp'),
        default=timezone.now,
        help_text=_('When the log entry was created')
    )
    
    level = models.CharField(
        _('level'),
        max_length=10,
        choices=LOG_LEVEL_CHOICES,
        default='info',
        help_text=_('Severity level of the log entry')
    )
    
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=LOG_CATEGORY_CHOICES,
        default='system',
        help_text=_('Category of the log entry')
    )
    
    message = models.TextField(
        _('message'),
        help_text=_('Log message')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='system_logs',
        help_text=_('User associated with this log entry (if applicable)')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True,
        help_text=_('IP address associated with this log entry')
    )
    
    user_agent = models.TextField(
        _('user agent'),
        null=True,
        blank=True,
        help_text=_('User agent associated with this log entry')
    )
    
    additional_data = models.JSONField(
        _('additional data'),
        null=True,
        blank=True,
        help_text=_('Additional JSON data related to this log entry')
    )
    
    class Meta:
        verbose_name = _('system log')
        verbose_name_plural = _('system logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"[{self.get_level_display()}] {self.timestamp}: {self.message[:50]}"


class BackupConfiguration(models.Model):
    """
    Model for configuring automated backups of the platform.
    """
    BACKUP_TYPE_CHOICES = [
        ('full', _('Full Backup')),
        ('database', _('Database Only')),
        ('files', _('Files Only')),
        ('custom', _('Custom'))
    ]
    
    FREQUENCY_CHOICES = [
        ('hourly', _('Hourly')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('custom', _('Custom Schedule'))
    ]
    
    STORAGE_CHOICES = [
        ('local', _('Local Storage')),
        ('s3', _('Amazon S3')),
        ('gcs', _('Google Cloud Storage')),
        ('azure', _('Azure Blob Storage')),
        ('sftp', _('SFTP Server'))
    ]
    
    name = models.CharField(
        _('name'),
        max_length=128,
        help_text=_('Name of this backup configuration')
    )
    
    enabled = models.BooleanField(
        _('enabled'),
        default=True,
        help_text=_('Whether this backup configuration is active')
    )
    
    backup_type = models.CharField(
        _('backup type'),
        max_length=20,
        choices=BACKUP_TYPE_CHOICES,
        default='full',
        help_text=_('Type of backup to perform')
    )
    
    frequency = models.CharField(
        _('frequency'),
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        help_text=_('How often to perform backups')
    )
    
    custom_cron = models.CharField(
        _('custom cron'),
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Custom cron expression for backup schedule (used if frequency is "custom")')
    )
    
    storage_type = models.CharField(
        _('storage type'),
        max_length=20,
        choices=STORAGE_CHOICES,
        default='local',
        help_text=_('Where to store the backup files')
    )
    
    storage_path = models.CharField(
        _('storage path'),
        max_length=255,
        default='backups/',
        help_text=_('Path or bucket where backups will be stored')
    )
    
    # Credentials (encrypted or stored securely)
    storage_credentials = models.JSONField(
        _('storage credentials'),
        null=True,
        blank=True,
        help_text=_('Credentials for the storage provider (encrypted)')
    )
    
    retention_count = models.IntegerField(
        _('retention count'),
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text=_('Number of backups to retain before deleting old ones')
    )
    
    compress = models.BooleanField(
        _('compress'),
        default=True,
        help_text=_('Whether to compress the backup files')
    )
    
    encrypt = models.BooleanField(
        _('encrypt'),
        default=False,
        help_text=_('Whether to encrypt the backup files')
    )
    
    notification_email = models.EmailField(
        _('notification email'),
        null=True,
        blank=True,
        help_text=_('Email to notify about backup status')
    )
    
    last_backup_time = models.DateTimeField(
        _('last backup time'),
        null=True,
        blank=True,
        help_text=_('When the last backup was performed')
    )
    
    last_backup_status = models.CharField(
        _('last backup status'),
        max_length=20,
        null=True,
        blank=True,
        help_text=_('Status of the last backup attempt')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When this configuration was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When this configuration was last updated')
    )
    
    class Meta:
        verbose_name = _('backup configuration')
        verbose_name_plural = _('backup configurations')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class MaintenanceWindow(models.Model):
    """
    Model for scheduling maintenance windows for the platform.
    """
    title = models.CharField(
        _('title'),
        max_length=128,
        help_text=_('Title of the maintenance window')
    )
    
    description = models.TextField(
        _('description'),
        help_text=_('Description of the maintenance activities')
    )
    
    start_time = models.DateTimeField(
        _('start time'),
        help_text=_('When the maintenance window begins')
    )
    
    end_time = models.DateTimeField(
        _('end time'),
        help_text=_('When the maintenance window ends')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('scheduled', _('Scheduled')),
            ('in_progress', _('In Progress')),
            ('completed', _('Completed')),
            ('cancelled', _('Cancelled'))
        ],
        default='scheduled',
        help_text=_('Current status of the maintenance window')
    )
    
    affects_registration = models.BooleanField(
        _('affects registration'),
        default=False,
        help_text=_('Whether the maintenance affects user registration')
    )
    
    affects_challenges = models.BooleanField(
        _('affects challenges'),
        default=False,
        help_text=_('Whether the maintenance affects challenge availability')
    )
    
    affects_submissions = models.BooleanField(
        _('affects submissions'),
        default=False,
        help_text=_('Whether the maintenance affects flag submissions')
    )
    
    affects_scoreboard = models.BooleanField(
        _('affects scoreboard'),
        default=False,
        help_text=_('Whether the maintenance affects scoreboard updates')
    )
    
    complete_downtime = models.BooleanField(
        _('complete downtime'),
        default=False,
        help_text=_('Whether the platform will be completely inaccessible')
    )
    
    visible_to_users = models.BooleanField(
        _('visible to users'),
        default=True,
        help_text=_('Whether to display a notice to users about this maintenance')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_maintenance_windows',
        help_text=_('User who scheduled this maintenance window')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When this maintenance window was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When this maintenance window was last updated')
    )
    
    class Meta:
        verbose_name = _('maintenance window')
        verbose_name_plural = _('maintenance windows')
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.title} ({self.start_time} to {self.end_time})"
    
    @property
    def is_active(self):
        """Check if the maintenance window is currently active."""
        now = timezone.now()
        return (
            self.start_time <= now <= self.end_time and 
            self.status == 'in_progress'
        )
    
    def activate(self):
        """Activate the maintenance window."""
        if self.status != 'scheduled':
            raise ValueError(_("Only scheduled maintenance windows can be activated"))
            
        now = timezone.now()
        if now < self.start_time:
            raise ValueError(_("Cannot activate a maintenance window before its start time"))
            
        self.status = 'in_progress'
        self.save(update_fields=['status'])
        
        # If complete downtime is enabled, put the platform in maintenance mode
        if self.complete_downtime:
            config = PlatformConfiguration.get_config()
            config.maintenance_mode = True
            config.maintenance_message = f"Maintenance in progress: {self.title}"
            config.save()
            
        return True
    
    def complete(self):
        """Mark the maintenance window as completed."""
        if self.status != 'in_progress':
            raise ValueError(_("Only in-progress maintenance windows can be completed"))
            
        self.status = 'completed'
        self.save(update_fields=['status'])
        
        # If complete downtime was enabled, disable maintenance mode
        if self.complete_downtime:
            config = PlatformConfiguration.get_config()
            config.maintenance_mode = False
            config.save()
            
        return True
