"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from utils.country_code import validate_country_code
from .avatar_models import AvatarOption
import uuid
import os

class UserManager(BaseUserManager):
    """
    Custom user manager for the User model with role-based creation methods.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a regular user with the given credentials"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_organizer(self, username, email, password=None, **extra_fields):
        """Create and save an organizer with the given credentials"""
        extra_fields.setdefault('type', 'organizer')
        extra_fields.setdefault('is_staff', True)
        
        return self.create_user(username, email, password, **extra_fields)
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a superuser (admin) with the given credentials"""
        extra_fields.setdefault('type', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, email, password, **extra_fields)


def user_avatar_path(instance, filename):
    """Generate a unique path for user avatars."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('avatars', filename)


class BaseUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based permission inheritance
    """
    USER_TYPE_CHOICES = [
        ('user', _('User')),
        ('organizer', _('Organizer')),
        ('admin', _('Admin'))
    ]

    GENDER_CHOICES = [
        ('male', _('Male')), 
        ('female', _('Female')), 
        ('none', _('Prefer not to say'))
    ]

    username = models.CharField(
        _('username'),
        max_length=150, 
        unique=True, 
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]{3,150}$',
                message=_('Enter a valid username.'),
                flags=0
            )
        ],
        help_text=_('Required. 3-150 characters. Letters, digits and @/./+/-/_ only.')
    )

    email = models.EmailField(_('email address'), unique=True)

    first_name = models.CharField(
        _('first name'),
        max_length=60, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s.]{2,60}$',
                message=_('Enter a valid first name.'),
                flags=0
            )
        ]
    )

    last_name = models.CharField(
        _('last name'),
        max_length=30, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s.]{2,30}$',
                message=_('Enter a valid last name.'),
                flags=0
            )
        ]
    )

    type = models.CharField(
        _('user type'),
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='user'
    )

    slug = models.SlugField(
        _('slug'),
        max_length=150, 
        unique=True, 
        blank=True, 
        null=True, 
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9-_]+$',
                message=_('Enter a valid slug.'),
                flags=0
            )
        ],
        help_text=_('URL-friendly identifier. Auto-generated if not provided.')
    )

    gender = models.CharField(
        _('gender'),
        max_length=10, 
        choices=GENDER_CHOICES, 
        default='none'
    )

    phone = models.CharField(
        _('phone number'),
        max_length=15, 
        unique=True, 
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_('Enter a valid phone number.'),
                flags=0
            )
        ]
    )

    country = models.CharField(
        _('country'),
        max_length=2, 
        validators=[validate_country_code], 
        blank=True, 
        null=True,
        default="IN"
    )

    # Profile fields
    avatar = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name=_("avatar"),
        blank=True,
        null=True,
        help_text=_("Profile avatar"),
    )

    # Avatar preferences
    preferred_avatar_theme = models.CharField(
        _("preferred avatar theme"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("User's preferred avatar theme category"),
    )

    # Legacy avatar field for backward compatibility
    custom_avatar = models.ImageField(
        _("custom avatar"),
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        help_text=_("Custom profile picture (legacy)"),
    )

    bio = models.TextField(
        _('biography'),
        blank=True,
        null=True,
        help_text=_('A short description about yourself')
    )

    affiliation = models.CharField(
        _('affiliation'),
        max_length=128,
        blank=True,
        null=True,
        help_text=_('School, company, or organization')
    )

    website = models.URLField(
        _('website'),
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text=_('Personal website or blog')
    )

    # Score and activity
    score = models.IntegerField(
        _('score'),
        default=0,
        help_text=_('Total points earned')
    )

    last_active = models.DateTimeField(
        _('last active'),
        default=timezone.now,
        help_text=_('Last time the user was active')
    )

    # Social media
    discord_id = models.CharField(
        _('discord ID'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Discord username')
    )

    github_username = models.CharField(
        _('github username'),
        max_length=39,
        blank=True,
        null=True,
        help_text=_('GitHub username')
    )

    linkedin_profile = models.URLField(
        _('linkedin profile'),
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text=_('LinkedIn profile URL')
    )

    twitter_username = models.CharField(
        _('twitter username'),
        max_length=15,
        blank=True,
        null=True,
        help_text=_('Twitter/X username without @')
    )

    # Status flags
    hidden = models.BooleanField(
        _('hidden profile'),
        default=False,
        help_text=_('Hide profile from public listings')
    )

    banned = models.BooleanField(
        _('banned'),
        default=False,
        help_text=_('User is banned from participating')
    )

    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Whether the email address has been verified')
    )

    secret_key = models.UUIDField(
        _('secret key'),
        default=uuid.uuid4,
        editable=False,
        help_text=_('Secret key for API access')
    )

    # Team relationship
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        related_name='members',
        blank=True,
        null=True,
        help_text=_('The team this user belongs to')
    )

    is_team_captain = models.BooleanField(
        _('team captain'),
        default=False,
        help_text=_('User is the captain of their team')
    )

    # Account fields
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    last_password_change = models.DateTimeField(_('last password change'), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    @property
    def avatar_url(self):
        """
        Get the appropriate avatar URL based on available avatar sources
        Order of precedence:
        1. Legacy custom uploaded avatar (highest priority)
        2. Selected avatar from predefined options
        3. Default placeholder avatar
        """
        import time

        timestamp = int(time.time())

        # Try legacy custom avatar first (highest priority)
        if self.custom_avatar:
            try:
                if self.custom_avatar.storage.exists(self.custom_avatar.name):
                    # Add timestamp to prevent caching
                    return f"{self.custom_avatar.url}?_t={timestamp}"
            except Exception as e:
                # If there's any error accessing the avatar, log it
                import logging

                logger = logging.getLogger("dctfd")
                logger.error(
                    f"Error retrieving custom avatar for user {self.id}: {str(e)}"
                )

        # Then try predefined avatar
        if hasattr(self, "avatar") and self.avatar and self.avatar.image:
            try:
                if self.avatar.image.storage.exists(self.avatar.image.name):
                    # Add timestamp to prevent caching
                    return f"{self.avatar.image.url}?_t={timestamp}"
                else:
                    # Log issue with missing avatar file
                    import logging

                    logger = logging.getLogger("dctfd")
                    logger.warning(
                        f"Avatar file missing for user {self.id}: {self.avatar.image.name}"
                    )
            except Exception as e:
                # If there's any error accessing the avatar, log it
                import logging

                logger = logging.getLogger("dctfd")
                logger.error(f"Error retrieving avatar for user {self.id}: {str(e)}")

        # Return default placeholder avatar
        try:
            default_avatar = AvatarOption.objects.filter(is_default=True).first()
            if default_avatar and default_avatar.image:
                # Add timestamp to prevent caching
                return f"{default_avatar.image.url}?_t={timestamp}"
        except Exception as e:
            import logging

            logger = logging.getLogger("dctfd")
            logger.error(f"Error retrieving default avatar: {str(e)}")
            pass

        # Fallback to static placeholder if no default is set
        return f"{settings.STATIC_URL}images/default_avatar.png"

    default_manager_name = "objects"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name

    def save(self, *args, **kwargs):
        """Override save method to automatically generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        """Override set_password to track password changes."""
        super().set_password(raw_password)
        self.last_password_change = timezone.now()

        # Don't save here as it will be done by the calling code
        # Just update the last_password_change field

    def update_password(self, raw_password, send_notification=True):
        """Update user password and send notification."""
        self.set_password(raw_password)
        self.save(update_fields=['password', 'last_password_change'])

        # Log the password change
        UserActivity.objects.create(
            user=self,
            activity_type='password_change',
            description="Password updated"
        )

        # Send password change notification
        if send_notification:
            try:
                from core.mailing import UserEmailService
                UserEmailService.send_password_changed_email(self)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password change notification: {str(e)}")

        return True

    @property
    def is_user(self):
        """Check if user has basic user permissions."""
        return self.type == 'user'

    @property
    def is_organizer(self):
        """Check if user has organizer permissions."""
        return self.type == 'organizer' or self.type == 'admin'

    @property
    def is_admin(self):
        """Check if user has admin permissions."""
        return self.type == 'admin'

    def update_last_active(self):
        """Update the last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def increment_score(self, points):
        """Increment user's score by the given points."""
        self.score += points
        self.save(update_fields=['score'])

    def get_avatar_url(self):
        """Return the URL of the user's avatar with a cache-busting timestamp."""
        import time

        # Add a timestamp to avoid browser caching
        timestamp = int(time.time())
        url = self.avatar_url

        # If the URL already contains a timestamp, don't add another one
        if "_t=" in url:
            return url

        # Add timestamp parameter to force browser to reload the image
        if "?" in url:
            return f"{url}&_t={timestamp}"
        else:
            return f"{url}?_t={timestamp}"

    def get_social_links(self):
        """Return a dictionary of the user's social media links."""
        links = {}
        if self.discord_id:
            links['discord'] = self.discord_id
        if self.github_username:
            links['github'] = f"https://github.com/{self.github_username}"
        if self.linkedin_profile:
            links['linkedin'] = self.linkedin_profile
        if self.twitter_username:
            links['twitter'] = f"https://twitter.com/{self.twitter_username}"
        if self.website:
            links['website'] = self.website
        return links

    def get_team_name(self):
        """Return the name of the user's team, if any."""
        if self.team:
            return self.team.name
        return None

    def get_team_members(self):
        """Return all members of the user's team, if any."""
        if self.team:
            return self.team.members.all()
        from django.apps import apps
        BaseUser = apps.get_model('users', 'BaseUser')
        return BaseUser.objects.none()

    def join_team(self, team, is_captain=False):
        """Join a team and send email notification."""
        old_team = self.team
        self.team = team
        self.is_team_captain = is_captain
        self.save(update_fields=['team', 'is_team_captain'])

        # Log the team join
        UserActivity.objects.create(
            user=self,
            activity_type='team_join',
            description=f"Joined team: {team.name}",
            team=team
        )

        # Send team join notification
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_team_join_confirmation(
                user=self,
                team=team
            )

            # Notify team captain if it's not the user themselves
            if not is_captain:
                captain = team.members.filter(is_team_captain=True).first()
                if captain and captain != self:
                    UserEmailService.send_team_member_joined_notification(
                        captain=captain,
                        member=self,
                        team=team
                    )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send team join notification: {str(e)}")

        return True

    def leave_team(self):
        """Leave the current team and send email notification."""
        if not self.team:
            return False

        team = self.team
        captain = team.members.filter(is_team_captain=True).first()

        # Store team info before removing
        team_name = team.name

        # Remove from team
        self.team = None
        self.is_team_captain = False
        self.save(update_fields=['team', 'is_team_captain'])

        # Log the team leave
        UserActivity.objects.create(
            user=self,
            activity_type='team_leave',
            description=f"Left team: {team_name}",
            team=team
        )

        # Send team leave notification
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_team_leave_confirmation(
                user=self,
                team_name=team_name
            )

            # Notify team captain if it's not the user themselves
            if captain and captain != self:
                UserEmailService.send_team_member_left_notification(
                    captain=captain,
                    member=self,
                    team=team
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send team leave notification: {str(e)}")

        return True

    def get_solved_challenges(self):
        """Return all challenges solved by the user."""
        # Filter only correct submissions
        return self.submissions.filter(is_correct=True).values_list('challenge', flat=True).distinct()

    def has_solved_challenge(self, challenge):
        """Check if the user has solved a specific challenge."""
        return self.submissions.filter(challenge=challenge, is_correct=True).exists()

    def get_rank(self, event=None):
        """Get the user's rank in an event or overall."""
        from django.db.models import Count, Max

        from django.apps import apps
        BaseUser = apps.get_model('users', 'BaseUser')
        query = BaseUser.objects.filter(is_active=True, banned=False)

        if event:
            # Filter users registered for this event
            query = query.filter(event_registrations__event=event, 
                                 event_registrations__status='approved')

        # Order by score and last solve time
        query = query.annotate(
            solve_count=Count('submissions', filter=models.Q(submissions__is_correct=True)),
            last_solve=Max('submissions__submitted_at', filter=models.Q(submissions__is_correct=True))
        ).order_by('-score', 'last_solve')

        # Find rank by iterating (not efficient for large datasets but accurate)
        for i, u in enumerate(query):
            if u.id == self.id:
                return i + 1

        return None

    def verify_email(self):
        """Mark the user's email as verified."""
        self.email_verified = True
        self.save(update_fields=['email_verified'])

        # Send email verification confirmation
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_welcome_email(self)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send welcome email after verification: {str(e)}")

        return True

    @property
    def can_be_banned(self):
        """
        Check if the user can be banned.

        Returns:
            bool: False for admin users (type='admin'), superusers, or staff users.
                  True for regular participants.

        Note:
            This prevents system administrators from being banned, which could
            lock them out of the system. Regular participants can still be banned.
        """
        return not (self.is_admin or self.is_superuser or self.is_staff)

    def ban(self, reason=None):
        """
        Ban the user from participating.

        Args:
            reason (str, optional): Reason for banning the user

        Raises:
            ValueError: If attempting to ban an admin user (admins, superusers, or staff)

        Note:
            Admin users (type='admin'), superusers, and staff users cannot be banned
            to prevent system administrators from being locked out.
        """
        # Prevent banning admin users - system protection
        if not self.can_be_banned:
            raise ValueError("Admin users cannot be banned")

        self.banned = True
        self.save(update_fields=['banned'])

        # Log the ban
        UserActivity.objects.create(
            user=self,
            activity_type='other',
            description=f"User banned. Reason: {reason or 'Not specified'}"
        )

        # Send ban notification email
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_account_status_email(
                user=self,
                status_type="banned",
                reason=reason
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send ban notification email: {str(e)}")

        return True

    def unban(self):
        """Unban the user."""
        self.banned = False
        self.save(update_fields=['banned'])

        # Log the unban
        UserActivity.objects.create(
            user=self,
            activity_type='other',
            description=f"User unbanned."
        )

        # Send unban notification email
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_account_status_email(
                user=self,
                status_type="unbanned"
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send unban notification email: {str(e)}")

        return True


# Role-specific proxy models
# We'll remove the proxy models for now
# We'll rely on the BaseUser model with type field for differentiation

# Add methods to BaseUser to get different user types
def get_regular_users():
    """Get all regular users."""
    from django.apps import apps
    BaseUser = apps.get_model('users', 'BaseUser')
    return BaseUser.objects.filter(type='user')

def get_organizers():
    """Get all organizers."""
    from django.apps import apps
    BaseUser = apps.get_model('users', 'BaseUser')
    return BaseUser.objects.filter(type='organizer')

def get_admins():
    """Get all admins."""
    from django.apps import apps
    BaseUser = apps.get_model('users', 'BaseUser')
    return BaseUser.objects.filter(type='admin')


# Additional user-related models
class UserActivity(models.Model):
    """
    Model to track user activity within the CTF platform.
    """
    ACTIVITY_TYPES = [
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('submission', _('Challenge Submission')),
        ('solve', _('Challenge Solve')),
        ('registration', _('Registration')),
        ('profile_update', _('Profile Update')),
        ('team_join', _('Team Join')),
        ('team_leave', _('Team Leave')),
        ('password_change', _('Password Change')),
        ('password_reset', _('Password Reset')),
        ('hint_unlock', _('Hint Unlock')),
        ('file_download', _('File Download')),
        ('other', _('Other'))
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
        help_text=_("User who performed the activity"),
    )

    activity_type = models.CharField(
        _('activity type'),
        max_length=20,
        choices=ACTIVITY_TYPES,
        help_text=_('Type of activity performed')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Additional details about the activity')
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
        help_text=_('Browser/client information')
    )

    timestamp = models.DateTimeField(
        _('timestamp'),
        default=timezone.now,
        help_text=_('When the activity occurred')
    )

    # Relations to other models
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_activities',
        help_text=_('Related challenge (if applicable)')
    )

    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_activities',
        help_text=_('Related team (if applicable)')
    )

    event = models.ForeignKey(
        'event.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_activities',
        help_text=_('Related event (if applicable)')
    )

    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"


class UserSetting(models.Model):
    """
    Model to store user preferences and settings.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
        help_text=_("User these settings belong to"),
    )

    notification_email = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Receive email notifications')
    )

    notification_browser = models.BooleanField(
        _('browser notifications'),
        default=True,
        help_text=_('Receive browser notifications')
    )

    theme = models.CharField(
        _('theme'),
        max_length=20,
        default='light',
        choices=[('light', _('Light')), ('dark', _('Dark')), ('system', _('System'))],
        help_text=_('UI theme preference')
    )

    language = models.CharField(
        _('language'),
        max_length=10,
        default='en',
        help_text=_('Preferred language')
    )

    timezone = models.CharField(
        _('timezone'),
        max_length=50,
        default='UTC',
        help_text=_('Preferred timezone')
    )

    show_solved_challenges = models.BooleanField(
        _('show solved challenges'),
        default=True,
        help_text=_('Show already solved challenges in challenge list')
    )

    leaderboard_visibility = models.BooleanField(
        _('leaderboard visibility'),
        default=True,
        help_text=_('Show user on public leaderboards')
    )

    two_factor_enabled = models.BooleanField(
        _('two-factor authentication'),
        default=False,
        help_text=_('Enable two-factor authentication')
    )

    hide_email = models.BooleanField(
        _('hide email'),
        default=True,
        help_text=_('Hide email from public profile')
    )

    hide_phone = models.BooleanField(
        _('hide phone'),
        default=True,
        help_text=_('Hide phone from public profile')
    )

    notify_team_join_request = models.BooleanField(
        _('notify on team join request'),
        default=True,
        help_text=_('Receive notification when someone requests to join your team')
    )

    notify_challenge_solve = models.BooleanField(
        _('notify on challenge solve'),
        default=True,
        help_text=_('Receive notification when a team member solves a challenge')
    )

    notify_event_announcement = models.BooleanField(
        _('notify on event announcement'),
        default=True,
        help_text=_('Receive notification for event announcements')
    )

    class Meta:
        verbose_name = _('user setting')
        verbose_name_plural = _('user settings')

    def __str__(self):
        return f"Settings for {self.user.username}"


# We don't need UserChallengeSolve anymore since we have Solve in challenges app
# But we'll create a compatibility layer to avoid breaking existing code
class UserChallengeSolve(models.Model):
    """
    Model to track challenge solves by users.
    DEPRECATED: Use challenges.Solve instead.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="solve_compat",
        help_text=_("User who solved the challenge"),
    )

    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.CASCADE,
        related_name='user_solves_compat',
        help_text=_('Challenge that was solved')
    )

    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        related_name='solves_compat',
        null=True,
        blank=True,
        help_text=_('Team the user belonged to when solving')
    )

    flag = models.TextField(
        _('flag'),
        help_text=_('The flag that was submitted')
    )

    points = models.IntegerField(
        _('points'),
        default=0,
        help_text=_('Points awarded for the solve')
    )

    first_blood = models.BooleanField(
        _('first blood'),
        default=False,
        help_text=_('Whether this was the first solve for this challenge')
    )

    timestamp = models.DateTimeField(
        _('timestamp'),
        default=timezone.now,
        help_text=_('When the challenge was solved')
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address from which the solve was submitted')
    )

    class Meta:
        verbose_name = _('user challenge solve')
        verbose_name_plural = _('user challenge solves')
        ordering = ['-timestamp']
        unique_together = ['user', 'challenge']

    def __str__(self):
        return f"{self.user.username} solved {self.challenge.name}"


class EmailVerification(models.Model):
    """
    Model for email verification tokens.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verifications',
        help_text=_('User who needs to verify their email')
    )
    
    token = models.UUIDField(
        _('token'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Verification token')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the token was created')
    )
    
    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('When the token expires')
    )
    
    used = models.BooleanField(
        _('used'),
        default=False,
        help_text=_('Whether the token has been used')
    )
    
    class Meta:
        verbose_name = _('email verification')
        verbose_name_plural = _('email verifications')
    
    def __str__(self):
        return f"Email verification for {self.user.email}"
    
    def save(self, *args, **kwargs):
        """Set expiration if not already set."""
        if not self.expires_at:
            # Token expires in 24 hours
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() > self.expires_at
    
    def use(self):
        """Mark the token as used and verify the user's email."""
        if not self.used and not self.is_expired:
            self.used = True
            self.save(update_fields=['used'])
            self.user.verify_email()
            return True
        return False


class PasswordReset(models.Model):
    """
    Model for password reset tokens.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_resets",
        help_text=_("User who requested a password reset"),
    )

    token = models.UUIDField(
        _('token'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Reset token')
    )

    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the token was created')
    )

    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('When the token expires')
    )

    used = models.BooleanField(
        _('used'),
        default=False,
        help_text=_('Whether the token has been used')
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address from which the reset was requested')
    )

    class Meta:
        verbose_name = _('password reset')
        verbose_name_plural = _('password resets')

    def __str__(self):
        return f"Password reset for {self.user.email}"

    def save(self, *args, **kwargs):
        """Set expiration if not already set."""
        if not self.expires_at:
            # Token expires in 1 hour
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() > self.expires_at

    def use(self):
        """Mark the token as used."""
        if not self.used and not self.is_expired:
            self.used = True
            self.save(update_fields=['used'])
            return True
        return False


class UserSession(models.Model):
    """
    Model to track user sessions.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text=_("User who owns this session"),
    )

    session_key = models.CharField(
        _('session key'),
        max_length=40,
        unique=True,
        help_text=_('Django session key')
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address from which the session was created')
    )

    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('Browser/client information')
    )

    device_type = models.CharField(
        _('device type'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Type of device used')
    )

    location = models.CharField(
        _('location'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Approximate location based on IP')
    )

    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the session was created')
    )

    last_active = models.DateTimeField(
        _('last active'),
        default=timezone.now,
        help_text=_('When the session was last active')
    )

    expired = models.BooleanField(
        _('expired'),
        default=False,
        help_text=_('Whether the session has expired')
    )

    class Meta:
        verbose_name = _('user session')
        verbose_name_plural = _('user sessions')
        ordering = ['-last_active']

    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address or 'unknown'}"

    def update_last_active(self):
        """Update the last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def expire(self):
        """Mark the session as expired."""
        self.expired = True
        self.save(update_fields=['expired'])
        return True
