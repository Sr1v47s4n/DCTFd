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
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Event(models.Model):
    """
    Model for CTF events.
    This is the central model that coordinates everything related to a specific CTF competition.
    """
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('registration', _('Registration Open')),
        ('running', _('Running')),
        ('paused', _('Paused')),
        ('finished', _('Finished')),
        ('archived', _('Archived'))
    ]
    
    ACCESS_CHOICES = [
        ('public', _('Public')),
        ('private', _('Private')),
        ('invite', _('Invite Only'))
    ]
    
    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Name of the event')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=120,
        unique=True,
        blank=True,
        help_text=_('URL-friendly name of the event')
    )
    
    description = models.TextField(
        _('description'),
        help_text=_('Full description of the event')
    )
    
    short_description = models.CharField(
        _('short description'),
        max_length=250,
        help_text=_('Brief description for listings and previews')
    )
    
    logo = models.ImageField(
        _('logo'),
        upload_to='event_logos/',
        blank=True,
        null=True,
        help_text=_('Event logo image')
    )
    
    banner = models.ImageField(
        _('banner'),
        upload_to='event_banners/',
        blank=True,
        null=True,
        help_text=_('Event banner image for headers')
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
        help_text=_('When registration opens')
    )
    
    registration_end = models.DateTimeField(
        _('registration end'),
        help_text=_('When registration closes')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text=_('Current status of the event')
    )
    
    access = models.CharField(
        _('access'),
        max_length=20,
        choices=ACCESS_CHOICES,
        default='public',
        help_text=_('Access control for the event')
    )
    
    is_visible = models.BooleanField(
        _('is visible'),
        default=True,
        help_text=_('Whether the event is visible in event listings')
    )
    
    scoreboard_visible = models.BooleanField(
        _('scoreboard visible'),
        default=True,
        help_text=_('Whether the scoreboard is visible to participants')
    )
    
    invite_code = models.UUIDField(
        _('invite code'),
        default=uuid.uuid4,
        editable=False,
        help_text=_('Code for invite-only events')
    )
    
    max_team_size = models.IntegerField(
        _('maximum team size'),
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_('Maximum members per team')
    )
    
    min_team_size = models.IntegerField(
        _('minimum team size'),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text=_('Minimum members per team')
    )
    
    allow_individual_participants = models.BooleanField(
        _('allow individual participants'),
        default=True,
        help_text=_('Whether users can participate without a team')
    )
    
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='event_organized_events',
        limit_choices_to={'type': 'organizer'},
        help_text=_('Users who can manage this event')
    )
    
    view_after_completion = models.BooleanField(
        _('view after completion'),
        default=True,
        help_text=_('Whether the event is viewable after it ends')
    )
    
    registration_email_template = models.TextField(
        _('registration email template'),
        blank=True,
        null=True,
        help_text=_('Email template for registration confirmations')
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
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events',
        help_text=_('User who created this event')
    )
    
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ['-start_time']
    
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_ongoing(self):
        """Return True if the event is currently running."""
        now = timezone.now()
        return (self.start_time <= now <= self.end_time) and not self.is_paused
    
    @property
    def is_upcoming(self):
        """Return True if the event has not started yet."""
        now = timezone.now()
        return now < self.start_time
    
    @property
    def is_ended(self):
        """Return True if the event has ended."""
        now = timezone.now()
        return now > self.end_time
    
    @property
    def is_active(self):
        """Check if the event is currently active."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'running'
    
    @property
    def is_registration_open(self):
        """Check if registration is currently open."""
        now = timezone.now()
        return (
            self.registration_start <= now <= self.registration_end and 
            self.status in ['planning', 'registration']
        )
    
    def update_status(self):
        """Update the event status based on current time."""
        now = timezone.now()
        
        if self.status == 'archived':
            return  # Don't change archived status
            
        if now < self.registration_start:
            self.status = 'planning'
        elif self.registration_start <= now < self.start_time:
            self.status = 'registration'
        elif self.start_time <= now <= self.end_time:
            if self.status != 'paused':
                self.status = 'running'
        elif now > self.end_time:
            self.status = 'finished'
            
        self.save(update_fields=['status'])
    
    def get_current_participants(self):
        """Get all users currently registered for this event."""
        return settings.AUTH_USER_MODEL.objects.filter(
            models.Q(event_registrations__event=self, event_registrations__status='approved') |
            models.Q(team__event_registrations__event=self, team__event_registrations__status='approved')
        ).distinct()
    
    def get_registered_teams(self):
        """Get all teams registered for this event."""
        from teams.models import Team
        return Team.objects.filter(
            event_registrations__event=self,
            event_registrations__status='approved'
        ).distinct()


class EventSettings(models.Model):
    """
    Model for customizing event-specific settings.
    """
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='settings',
        help_text=_('Event these settings belong to')
    )

    # Scoring settings
    allow_zero_point_challenges = models.BooleanField(
        _('allow zero point challenges'),
        default=True,
        help_text=_('Whether to allow challenges with zero points')
    )

    use_dynamic_scoring = models.BooleanField(
        _('use dynamic scoring'),
        default=False,
        help_text=_('Whether to use dynamic scoring based on solves')
    )

    # Time settings
    freeze_scoreboard_at = models.DateTimeField(
        _('freeze scoreboard at'),
        blank=True,
        null=True,
        help_text=_('When to freeze the scoreboard updates')
    )

    # Registration settings
    require_email_verification = models.BooleanField(
        _('require email verification'),
        default=True,
        help_text=_('Whether users must verify email to participate')
    )

    auto_approve_participants = models.BooleanField(
        _('auto approve participants'),
        default=True,
        help_text=_('Whether to automatically approve registrations')
    )

    allow_team_creation = models.BooleanField(
        _('allow team creation'),
        default=True,
        help_text=_('Whether users can create teams')
    )

    allow_team_joining = models.BooleanField(
        _('allow team joining'),
        default=True,
        help_text=_('Whether users can join teams')
    )

    # Custom field settings
    enable_user_custom_fields = models.BooleanField(
        _("enable user custom fields"),
        default=False,
        help_text=_("Whether to collect custom fields during user registration"),
    )

    enable_team_custom_fields = models.BooleanField(
        _("enable team custom fields"),
        default=False,
        help_text=_("Whether to collect custom fields during team creation"),
    )

    # Feature toggles
    show_challenges_before_start = models.BooleanField(
        _('show challenges before start'),
        default=False,
        help_text=_('Whether to show challenges before event starts')
    )

    allow_challenge_feedback = models.BooleanField(
        _('allow challenge feedback'),
        default=True,
        help_text=_('Whether users can submit feedback on challenges')
    )

    enable_team_communication = models.BooleanField(
        _('enable team communication'),
        default=True,
        help_text=_('Whether to enable team chat features')
    )

    enable_hints = models.BooleanField(
        _('enable hints'),
        default=True,
        help_text=_('Whether hints are available for challenges')
    )

    # Custom fields settings
    enable_user_custom_fields = models.BooleanField(
        _("enable user custom fields"),
        default=False,
        help_text=_(
            "Whether to collect additional custom information during user registration"
        ),
    )

    enable_team_custom_fields = models.BooleanField(
        _("enable team custom fields"),
        default=False,
        help_text=_(
            "Whether to collect additional custom information during team creation"
        ),
    )

    # Appearance settings
    theme = models.CharField(
        _('theme'),
        max_length=50,
        default='default',
        help_text=_('Theme for the event pages')
    )

    custom_css = models.TextField(
        _('custom CSS'),
        blank=True,
        null=True,
        help_text=_('Custom CSS for event pages')
    )

    custom_js = models.TextField(
        _('custom JavaScript'),
        blank=True,
        null=True,
        help_text=_('Custom JavaScript for event pages')
    )

    # Limits
    submission_cooldown = models.IntegerField(
        _('submission cooldown'),
        default=5,
        help_text=_('Seconds between flag submissions')
    )

    max_submissions_per_minute = models.IntegerField(
        _('max submissions per minute'),
        default=10,
        help_text=_('Maximum flag submissions per minute')
    )

    class Meta:
        verbose_name = _('event settings')
        verbose_name_plural = _('event settings')

    def __str__(self):
        return f"Settings for {self.event.name}"


class EventPage(models.Model):
    """
    Model for custom pages related to an event.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text=_('Event this page belongs to')
    )
    
    title = models.CharField(
        _('title'),
        max_length=100,
        help_text=_('Page title')
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=120,
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
    
    registration_required = models.BooleanField(
        _('registration required'),
        default=False,
        help_text=_('Whether event registration is required to view')
    )
    
    order = models.IntegerField(
        _('order'),
        default=0,
        help_text=_('Order in navigation')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the page was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the page was last updated')
    )
    
    class Meta:
        verbose_name = _('event page')
        verbose_name_plural = _('event pages')
        unique_together = [['event', 'slug']]
        ordering = ['event', 'order', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.event.name})"
    
    def save(self, *args, **kwargs):
        """Override save to generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class EventAnnouncement(models.Model):
    """
    Model for announcements related to an event.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text=_('Event this announcement belongs to')
    )
    
    title = models.CharField(
        _('title'),
        max_length=100,
        help_text=_('Announcement title')
    )
    
    content = models.TextField(
        _('content'),
        help_text=_('Announcement content (supports Markdown)')
    )
    
    is_important = models.BooleanField(
        _('is important'),
        default=False,
        help_text=_('Whether this is an important announcement')
    )
    
    publish_time = models.DateTimeField(
        _('publish time'),
        default=timezone.now,
        help_text=_('When to publish the announcement')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_event_announcements',
        help_text=_('User who created this announcement')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
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
        return f"{self.title} ({self.event.name})"
    
    @property
    def is_published(self):
        """Check if the announcement is published."""
        return timezone.now() >= self.publish_time


class Scoreboard(models.Model):
    """
    Model for storing the scoreboard state for an event.
    """
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='scoreboard',
        help_text=_('Event this scoreboard belongs to')
    )
    
    last_updated = models.DateTimeField(
        _('last updated'),
        default=timezone.now,
        help_text=_('When the scoreboard was last updated')
    )
    
    is_frozen = models.BooleanField(
        _('is frozen'),
        default=False,
        help_text=_('Whether the scoreboard is currently frozen')
    )
    
    freeze_time = models.DateTimeField(
        _('freeze time'),
        blank=True,
        null=True,
        help_text=_('When the scoreboard was frozen')
    )
    
    class Meta:
        verbose_name = _('scoreboard')
        verbose_name_plural = _('scoreboards')
    
    def __str__(self):
        return f"Scoreboard for {self.event.name}"
    
    def freeze(self):
        """Freeze the scoreboard."""
        self.is_frozen = True
        self.freeze_time = timezone.now()
        self.save(update_fields=['is_frozen', 'freeze_time'])
        return True
    
    def unfreeze(self):
        """Unfreeze the scoreboard."""
        self.is_frozen = False
        self.last_updated = timezone.now()
        self.save(update_fields=['is_frozen', 'last_updated'])
        return True
    
    def update(self):
        """Update the scoreboard."""
        if not self.is_frozen:
            self.last_updated = timezone.now()
            self.save(update_fields=['last_updated'])
        return not self.is_frozen


class ScoreboardEntry(models.Model):
    """
    Model for individual entries on the scoreboard.
    """
    scoreboard = models.ForeignKey(
        Scoreboard,
        on_delete=models.CASCADE,
        related_name='entries',
        help_text=_('Scoreboard this entry belongs to')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='scoreboard_entries',
        help_text=_('Team this entry represents')
    )
    
    score = models.IntegerField(
        _('score'),
        default=0,
        help_text=_('Team\'s total score')
    )
    
    last_score_time = models.DateTimeField(
        _('last score time'),
        default=timezone.now,
        help_text=_('When the team last scored points')
    )
    
    rank = models.IntegerField(
        _('rank'),
        default=0,
        help_text=_('Team\'s current rank')
    )
    
    challenge_count = models.IntegerField(
        _('challenge count'),
        default=0,
        help_text=_('Number of challenges solved')
    )
    
    is_eligible = models.BooleanField(
        _('is eligible'),
        default=True,
        help_text=_('Whether the team is eligible for prizes/ranking')
    )
    
    class Meta:
        verbose_name = _('scoreboard entry')
        verbose_name_plural = _('scoreboard entries')
        ordering = ['-score', 'last_score_time']
        unique_together = [['scoreboard', 'team']]
    
    def __str__(self):
        return f"{self.team.name} - {self.score} ({self.scoreboard.event.name})"


class EventRegistration(models.Model):
    """
    Model for tracking user registrations for events.
    """
    STATUS_CHOICES = [
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
        related_name='user_event_registrations',
        help_text=_('User registering for the event')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='team_event_registrations',
        help_text=_('Team registering for the event (if applicable)')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Registration status')
    )
    
    registered_at = models.DateTimeField(
        _('registered at'),
        default=timezone.now,
        help_text=_('When the registration was submitted')
    )
    
    approved_at = models.DateTimeField(
        _('approved at'),
        blank=True,
        null=True,
        help_text=_('When the registration was approved')
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_registrations',
        help_text=_('User who approved this registration')
    )
    
    is_eligible = models.BooleanField(
        _('is eligible'),
        default=True,
        help_text=_('Whether the registration is eligible for prizes')
    )
    
    extra_data = models.JSONField(
        _('extra data'),
        blank=True,
        null=True,
        help_text=_('Additional registration data')
    )
    
    class Meta:
        verbose_name = _('event registration')
        verbose_name_plural = _('event registrations')
        unique_together = [['event', 'user']]
        ordering = ['event', '-registered_at']
    
    def __str__(self):
        team_info = f" with {self.team.name}" if self.team else ""
        return f"{self.user.username}{team_info} - {self.event.name}"
    
    def approve(self, approver=None):
        """Approve this registration."""
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = approver
        self.save(update_fields=['status', 'approved_at', 'approved_by'])
        return True
    
    def reject(self):
        """Reject this registration."""
        self.status = 'rejected'
        self.save(update_fields=['status'])
        return True
    
    def waitlist(self):
        """Waitlist this registration."""
        self.status = 'waitlisted'
        self.save(update_fields=['status'])
        return True


class EventActivity(models.Model):
    """
    Model for tracking event-related activities.
    """
    ACTIVITY_TYPES = [
        ('registration', _('Registration')),
        ('login', _('Login')),
        ('solve', _('Challenge Solve')),
        ('hint', _('Hint Unlock')),
        ('submission', _('Flag Submission')),
        ('announcement', _('Announcement')),
        ('score_change', _('Score Change')),
        ('team_join', _('Team Join')),
        ('team_leave', _('Team Leave')),
        ('admin_action', _('Admin Action'))
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='activities',
        help_text=_('Event this activity belongs to')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='event_activities',
        help_text=_('User associated with this activity')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='event_activities',
        help_text=_('Team associated with this activity')
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=ACTIVITY_TYPES,
        help_text=_('Type of activity')
    )
    
    timestamp = models.DateTimeField(
        _('timestamp'),
        default=timezone.now,
        help_text=_('When the activity occurred')
    )
    
    data = models.JSONField(
        _('data'),
        blank=True,
        null=True,
        help_text=_('Additional activity data')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address associated with this activity')
    )
    
    class Meta:
        verbose_name = _('event activity')
        verbose_name_plural = _('event activities')
        ordering = ['-timestamp']
    
    def __str__(self):
        user_info = f" by {self.user.username}" if self.user else ""
        team_info = f" ({self.team.name})" if self.team else ""
        return f"{self.get_type_display()}{user_info}{team_info} - {self.event.name}"
