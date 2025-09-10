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
from django.core.validators import RegexValidator, URLValidator, MinValueValidator, MaxValueValidator


class Event(models.Model):
    """
    Model for CTF events managed by organizers.
    """
    EVENT_STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('registration', _('Registration Open')),
        ('ongoing', _('Ongoing')),
        ('completed', _('Completed')),
        ('archived', _('Archived'))
    ]
    
    name = models.CharField(
        _('event name'),
        max_length=128,
        unique=True,
        help_text=_('Name of the CTF event')
    )
    
    description = models.TextField(
        _('description'),
        help_text=_('Description of the event')
    )
    
    short_description = models.CharField(
        _('short description'),
        max_length=255,
        help_text=_('Brief description for listings and previews')
    )
    
    logo = models.ImageField(
        _('logo'),
        upload_to='event_logos/',
        blank=True,
        null=True,
        help_text=_('Event logo')
    )
    
    banner = models.ImageField(
        _('banner'),
        upload_to='event_banners/',
        blank=True,
        null=True,
        help_text=_('Event banner for website header')
    )
    
    start_time = models.DateTimeField(
        _('start time'),
        help_text=_('When the event begins')
    )
    
    end_time = models.DateTimeField(
        _('end time'),
        help_text=_('When the event ends')
    )
    
    registration_start = models.DateTimeField(
        _('registration start'),
        help_text=_('When registration for the event begins')
    )
    
    registration_end = models.DateTimeField(
        _('registration end'),
        help_text=_('When registration for the event ends')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=EVENT_STATUS_CHOICES,
        default='draft',
        help_text=_('Current status of the event')
    )
    
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='organizer_organized_events',
        limit_choices_to={'type': 'organizer'},
        help_text=_('Users with organizer permissions for this event')
    )
    
    public = models.BooleanField(
        _('public'),
        default=True,
        help_text=_('Whether the event is visible to all users')
    )
    
    registration_open = models.BooleanField(
        _('registration open'),
        default=False,
        help_text=_('Whether users can register for the event')
    )
    
    max_team_size = models.IntegerField(
        _('maximum team size'),
        default=5,
        help_text=_('Maximum number of members per team')
    )
    
    min_team_size = models.IntegerField(
        _('minimum team size'),
        default=1,
        help_text=_('Minimum number of members per team')
    )
    
    allow_individual_participants = models.BooleanField(
        _('allow individual participants'),
        default=True,
        help_text=_('Whether users can participate without a team')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the event was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the event was last updated')
    )
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['-start_time']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        """Check if the event is currently active."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'ongoing'
    
    @property
    def is_registration_open(self):
        """Check if registration is currently open."""
        now = timezone.now()
        return (
            self.registration_start <= now <= self.registration_end and 
            self.registration_open and
            self.status in ['registration', 'published']
        )
    
    def update_status(self):
        """Update the event status based on current time."""
        now = timezone.now()
        
        if self.status == 'archived':
            return  # Don't change archived status
            
        if now < self.registration_start:
            if self.status != 'draft':
                self.status = 'published'
        elif self.registration_start <= now <= self.registration_end:
            self.status = 'registration'
        elif self.start_time <= now <= self.end_time:
            self.status = 'ongoing'
        elif now > self.end_time:
            self.status = 'completed'
            
        self.save(update_fields=['status'])


class EventAnnouncement(models.Model):
    """
    Model for announcements made by organizers about events.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text=_('Event this announcement is for')
    )
    
    title = models.CharField(
        _('title'),
        max_length=128,
        help_text=_('Announcement title')
    )
    
    content = models.TextField(
        _('content'),
        help_text=_('Announcement content')
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='authored_event_announcements',
        help_text=_('User who created the announcement')
    )
    
    important = models.BooleanField(
        _('important'),
        default=False,
        help_text=_('Whether this is an important announcement')
    )
    
    publish_time = models.DateTimeField(
        _('publish time'),
        default=timezone.now,
        help_text=_('When to publish the announcement')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the announcement was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the announcement was last updated')
    )
    
    class Meta:
        verbose_name = _('event announcement')
        verbose_name_plural = _('event announcements')
        ordering = ['-publish_time']
    
    def __str__(self):
        return f"{self.event.name} - {self.title}"
    
    @property
    def is_published(self):
        """Check if the announcement is published."""
        return timezone.now() >= self.publish_time


class EventSettings(models.Model):
    """
    Model for event-specific settings.
    """
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text=_('Event these settings belong to')
    )
    
    # Scoring settings
    use_dynamic_scoring = models.BooleanField(
        _('use dynamic scoring'),
        default=False,
        help_text=_('Whether challenge points decrease as more teams solve them')
    )
    
    # Visibility settings
    show_scoreboard = models.BooleanField(
        _('show scoreboard'),
        default=True,
        help_text=_('Whether the scoreboard is visible to participants')
    )
    
    freeze_scoreboard_at = models.DateTimeField(
        _('freeze scoreboard at'),
        null=True,
        blank=True,
        help_text=_('When to freeze the scoreboard (optional)')
    )
    
    show_challenge_details = models.BooleanField(
        _('show challenge details'),
        default=True,
        help_text=_('Whether to show challenge details like solves and category')
    )
    
    # Registration settings
    require_email_verification = models.BooleanField(
        _('require email verification'),
        default=True,
        help_text=_('Whether users must verify their email before participating')
    )
    
    allow_team_changes = models.BooleanField(
        _('allow team changes'),
        default=True,
        help_text=_('Whether participants can change teams during the event')
    )
    
    team_change_cutoff = models.DateTimeField(
        _('team change cutoff'),
        null=True,
        blank=True,
        help_text=_('Deadline after which team changes are not allowed (optional)')
    )
    
    # Feature toggles
    enable_hints = models.BooleanField(
        _('enable hints'),
        default=True,
        help_text=_('Whether hints are available for challenges')
    )
    
    enable_team_chat = models.BooleanField(
        _('enable team chat'),
        default=True,
        help_text=_('Whether team members can chat with each other')
    )
    
    enable_challenge_feedback = models.BooleanField(
        _('enable challenge feedback'),
        default=True,
        help_text=_('Whether participants can provide feedback on challenges')
    )
    
    # Miscellaneous
    theme = models.CharField(
        _('theme'),
        max_length=50,
        default='default',
        help_text=_('Visual theme for the event')
    )
    
    class Meta:
        verbose_name = _('event settings')
        verbose_name_plural = _('event settings')
    
    def __str__(self):
        return f"Settings for {self.event.name}"


class EventRegistration(models.Model):
    """
    Model for tracking registrations to events.
    """
    REGISTRATION_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('waitlisted', _('Waitlisted'))
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        help_text=_('Event being registered for')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organizer_event_registrations',
        help_text=_('User registering for the event')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organizer_event_registrations',
        help_text=_('Team registering for the event (if applicable)')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=REGISTRATION_STATUS_CHOICES,
        default='pending',
        help_text=_('Current status of the registration')
    )
    
    registered_at = models.DateTimeField(
        _('registered at'),
        default=timezone.now,
        help_text=_('When the registration was submitted')
    )
    
    notes = models.TextField(
        _('notes'),
        blank=True,
        null=True,
        help_text=_('Additional notes or comments')
    )
    
    # Optional information
    eligibility_confirmed = models.BooleanField(
        _('eligibility confirmed'),
        default=False,
        help_text=_('Whether the participant has confirmed eligibility for prizes')
    )
    
    # Special fields for organizer notes
    organizer_notes = models.TextField(
        _('organizer notes'),
        blank=True,
        null=True,
        help_text=_('Private notes for organizers')
    )
    
    class Meta:
        verbose_name = _('event registration')
        verbose_name_plural = _('event registrations')
        unique_together = ['event', 'user']
        ordering = ['event', 'registered_at']
    
    def __str__(self):
        team_info = f" ({self.team.name})" if self.team else ""
        return f"{self.user.username}{team_info} - {self.event.name}"
    
    def approve(self):
        """Approve the registration."""
        self.status = 'approved'
        self.save(update_fields=['status'])
        
        # Create notification or send email
        return True
    
    def reject(self):
        """Reject the registration."""
        self.status = 'rejected'
        self.save(update_fields=['status'])
        
        # Create notification or send email
        return True
    
    def waitlist(self):
        """Put the registration on the waitlist."""
        self.status = 'waitlisted'
        self.save(update_fields=['status'])
        
        # Create notification or send email
        return True


class OrganizerTaskAssignment(models.Model):
    """
    Model for assigning tasks to organizers for an event.
    """
    TASK_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('blocked', _('Blocked')),
        ('cancelled', _('Cancelled'))
    ]
    
    TASK_PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical'))
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='organizer_tasks',
        help_text=_('Event this task is for')
    )
    
    title = models.CharField(
        _('title'),
        max_length=128,
        help_text=_('Task title')
    )
    
    description = models.TextField(
        _('description'),
        help_text=_('Task description')
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text=_('Organizer assigned to this task')
    )
    
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        help_text=_('User who assigned this task')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default='pending',
        help_text=_('Current status of the task')
    )
    
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=TASK_PRIORITY_CHOICES,
        default='medium',
        help_text=_('Priority level of the task')
    )
    
    due_date = models.DateTimeField(
        _('due date'),
        null=True,
        blank=True,
        help_text=_('When the task should be completed by')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the task was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the task was last updated')
    )
    
    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('When the task was completed')
    )
    
    class Meta:
        verbose_name = _('organizer task assignment')
        verbose_name_plural = _('organizer task assignments')
        ordering = ['-priority', 'due_date', 'created_at']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"
    
    def mark_completed(self):
        """Mark the task as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        return True
    
    @property
    def is_overdue(self):
        """Check if the task is overdue."""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date and self.status != 'completed'
