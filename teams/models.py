"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import RegexValidator, URLValidator
from django.conf import settings
from utils.country_code import validate_country_code
from users.avatar_models import AvatarOption
import uuid
import time

class Team(models.Model):
    """
    Team model for CTF competitions.
    """
    TEAM_STATUS_CHOICES = [
        ('active', _('Active')),
        ('disabled', _('Disabled')),
        ('banned', _('Banned')),
        ('pending', _('Pending Approval'))
    ]

    name = models.CharField(
        _('team name'),
        max_length=128,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w\s.-]{3,128}$',
                message=_('Enter a valid team name.'),
                flags=0
            )
        ],
        help_text=_('Required. 3-128 characters. Letters, digits, spaces, and ./- only.')
    )

    password = models.CharField(
        _('team password'),
        max_length=128,
        blank=True,
        null=True,
        help_text=_('Password required to join the team. Leave blank for invite-only teams.')
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

    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Team description or bio')
    )

    logo = models.ImageField(
        _("logo"),
        upload_to="team_logos/",
        blank=True,
        null=True,
        help_text=_("Team logo or avatar (legacy)"),
    )

    avatar = models.ForeignKey(
        AvatarOption,
        on_delete=models.SET_NULL,
        related_name="teams",
        verbose_name=_("avatar"),
        blank=True,
        null=True,
        help_text=_("Team avatar"),
    )

    # Avatar preferences
    preferred_avatar_theme = models.CharField(
        _("preferred avatar theme"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Team's preferred avatar theme category"),
    )

    website = models.URLField(
        _('website'),
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text=_('Team website or blog')
    )

    country = models.CharField(
        _('country'),
        max_length=2,
        validators=[validate_country_code],
        blank=True,
        null=True,
        default="IN",
        help_text=_('Country code (ISO 3166-1 alpha-2)')
    )

    affiliation = models.CharField(
        _('affiliation'),
        max_length=128,
        blank=True,
        null=True,
        help_text=_('School, company, or organization')
    )

    discord_server = models.CharField(
        _('discord server'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Discord server invite code')
    )

    github_organization = models.CharField(
        _('github organization'),
        max_length=39,
        blank=True,
        null=True,
        help_text=_('GitHub organization name')
    )

    invite_code = models.UUIDField(
        _('invite code'),
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_('Code for users to join the team')
    )

    max_members = models.IntegerField(
        _('maximum members'),
        default=5,
        help_text=_('Maximum number of members allowed')
    )

    score = models.IntegerField(
        _('score'),
        default=0,
        help_text=_('Total team score')
    )

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TEAM_STATUS_CHOICES,
        default='active',
        help_text=_('Team status')
    )

    captain = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='captain_of',
        blank=True,
        null=True,
        help_text=_('Team captain/leader')
    )

    hidden = models.BooleanField(
        _('hidden'),
        default=False,
        help_text=_('Hide team from public listings')
    )

    locked = models.BooleanField(
        _('locked'),
        default=False,
        help_text=_('Prevent changes to team membership')
    )

    eligible = models.BooleanField(
        _('eligible'),
        default=True,
        help_text=_('Eligible for prizes and official rankings')
    )

    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the team was created')
    )

    last_active = models.DateTimeField(
        _('last active'),
        default=timezone.now,
        help_text=_('Last time any team member was active')
    )

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        ordering = ['-score', 'created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to automatically generate slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def member_count(self):
        """Get the number of team members."""
        return self.members.count()

    @property
    def is_full(self):
        """Check if the team has reached its maximum members."""
        # First try to get the value from team settings
        try:
            max_members = self.team_settings.max_members
        except TeamSettings.DoesNotExist:
            # Fall back to the team's default value
            max_members = self.max_members

        return self.member_count >= max_members

    def update_last_active(self):
        """Update the last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def get_logo_url(self):
        """Return the URL of the team's logo or a default if none exists."""
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return f"https://www.gravatar.com/avatar/{hash(self.name)}?d=identicon&s=200"

    @property
    def avatar_url(self):
        """
        Get the appropriate avatar URL based on available avatar sources
        Order of precedence:
        1. Legacy logo (highest priority)
        2. Selected avatar from predefined options
        3. Default placeholder avatar
        """
        timestamp = int(time.time())

        # Try legacy logo first (highest priority)
        if self.logo and hasattr(self.logo, "url"):
            try:
                if self.logo.storage.exists(self.logo.name):
                    # Add timestamp to prevent caching
                    return f"{self.logo.url}?_t={timestamp}"
            except Exception as e:
                # If there's any error accessing the logo, log it
                import logging

                logger = logging.getLogger("dctfd")
                logger.error(f"Error retrieving team logo for team {self.id}: {str(e)}")

        # Then try predefined avatar
        if self.avatar and self.avatar.image:
            try:
                if self.avatar.image.storage.exists(self.avatar.image.name):
                    # Add timestamp to prevent caching
                    return f"{self.avatar.image.url}?_t={timestamp}"
                else:
                    # Log issue with missing avatar file
                    import logging

                    logger = logging.getLogger("dctfd")
                    logger.warning(
                        f"Avatar file missing for team {self.id}: {self.avatar.image.name}"
                    )
            except Exception as e:
                # If there's any error accessing the avatar, log it
                import logging

                logger = logging.getLogger("dctfd")
                logger.error(f"Error retrieving avatar for team {self.id}: {str(e)}")

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

        # Fallback to static placeholder or gravatar
        return f"https://www.gravatar.com/avatar/{hash(self.name)}?d=identicon&s=200"

    def get_avatar_url(self):
        """Return the URL of the team's avatar with a cache-busting timestamp."""
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

    def generate_new_invite_code(self):
        """Generate a new invite code for the team."""
        self.invite_code = uuid.uuid4()
        self.save(update_fields=['invite_code'])
        return self.invite_code

    def increment_score(self, points):
        """Increment team's score by the given points."""
        self.score += points
        self.save(update_fields=['score'])

    def add_member(self, user):
        """Add a user to the team if possible."""
        if self.is_full:
            raise ValueError(_("Team is already at maximum capacity"))

        if user.team:
            raise ValueError(_("User is already in a team"))

        if self.locked:
            raise ValueError(_("Team is locked and not accepting new members"))

        # Check team settings for auto-acceptance
        try:
            settings = self.team_settings
            if settings.require_captain_approval and not user.is_admin:
                # Create a pending request instead of directly adding
                join_request, created = TeamJoinRequest.objects.get_or_create(
                    team=self,
                    user=user
                )
                if created:
                    return "pending"
                return "pending_exists"
        except TeamSettings.DoesNotExist:
            pass  # No settings, proceed with direct add

        user.team = self
        user.save(update_fields=['team'])

        # Create a record of this join
        TeamMembershipLog.objects.create(
            team=self,
            user=user,
            action='join'
        )

        return True

    @classmethod
    def create_team(cls, name, captain, password=None, max_members=5, description=None):
        """Create a new team with the given captain."""
        if captain.team:
            raise ValueError(_("User is already in a team"))

        # Create the team
        team = cls(
            name=name,
            description=description,
            max_members=max_members,
            status='active'
        )

        # Set password if provided
        if password:
            team.set_password(password)

        team.save()

        # Set the captain
        team.captain = captain
        team.save(update_fields=['captain'])

        # Add captain as a member
        captain.team = team
        captain.is_team_captain = True
        captain.save(update_fields=['team', 'is_team_captain'])

        # Create team settings
        TeamSettings.objects.create(
            team=team,
            require_captain_approval=True,
            max_members=max_members
        )

        # Log the team creation
        TeamMembershipLog.objects.create(
            team=team,
            user=captain,
            action='join',
            note='Team created'
        )

        return team

    def remove_member(self, user):
        """Remove a user from the team."""
        if user.team != self:
            raise ValueError(_("User is not a member of this team"))

        if user == self.captain:
            raise ValueError(_("Captain cannot leave the team without assigning a new captain"))

        user.team = None
        user.is_team_captain = False
        user.save(update_fields=['team', 'is_team_captain'])

        # Create a record of this removal
        TeamMembershipLog.objects.create(
            team=self,
            user=user,
            action='leave'
        )

        return True

    def change_captain(self, new_captain):
        """Change the team captain."""
        if new_captain.team != self:
            raise ValueError(_("New captain must be a member of this team"))

        # Update the old captain if there is one
        if self.captain:
            old_captain = self.captain
            old_captain.is_team_captain = False
            old_captain.save(update_fields=['is_team_captain'])

        # Set the new captain
        self.captain = new_captain
        new_captain.is_team_captain = True
        new_captain.save(update_fields=['is_team_captain'])
        self.save(update_fields=['captain'])

        # Create a log entry
        TeamMembershipLog.objects.create(
            team=self,
            user=new_captain,
            action='captain_change'
        )

        return True

    def verify_password(self, password):
        """Verify the team password."""
        from django.contrib.auth.hashers import check_password

        if not self.password:
            return False

        return check_password(password, self.password)

    def set_password(self, password):
        """Set the team password with proper hashing."""
        from django.contrib.auth.hashers import make_password

        self.password = make_password(password)
        self.save(update_fields=['password'])

    def join_with_password(self, user, password):
        """Join a team using a password."""
        if self.is_full:
            raise ValueError(_("Team is already at maximum capacity"))

        if user.team:
            raise ValueError(_("User is already in a team"))

        if not self.verify_password(password):
            raise ValueError(_("Incorrect team password"))

        if self.locked:
            raise ValueError(_("Team is locked and not accepting new members"))

        # Add user to the team
        user.team = self
        user.save(update_fields=['team'])

        # Create a record of this join
        TeamMembershipLog.objects.create(
            team=self,
            user=user,
            action='join_via_password'
        )

        return True

    def disband(self):
        """Disband the team, removing all members."""
        # Remove all members
        for user in self.members.all():
            user.team = None
            user.is_team_captain = False
            user.save(update_fields=['team', 'is_team_captain'])

            # Log the removal
            TeamMembershipLog.objects.create(
                team=self,
                user=user,
                action='team_disbanded'
            )

        # Mark the team as disbanded
        self.status = 'disabled'
        self.save(update_fields=['status'])

        return True

    def join_with_invite_code(self, user, invite_code):
        """Join a team using an invite code."""
        if self.is_full:
            raise ValueError(_("Team is already at maximum capacity"))

        if user.team:
            raise ValueError(_("User is already in a team"))

        if str(self.invite_code) != str(invite_code):
            raise ValueError(_("Invalid invite code"))

        if self.locked:
            raise ValueError(_("Team is locked and not accepting new members"))

        # Add user to the team
        user.team = self
        user.save(update_fields=['team'])

        # Create a record of this join
        TeamMembershipLog.objects.create(
            team=self,
            user=user,
            action='join_via_code'
        )

        return True


class TeamInvite(models.Model):
    """
    Model for tracking team invitations.
    """
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='invites',
        help_text=_('Team sending the invitation')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_invites',
        help_text=_('User being invited')
    )
    
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='sent_team_invites',
        null=True,
        blank=True,
        help_text=_('User who sent the invitation')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the invitation was created')
    )
    
    expires_at = models.DateTimeField(
        _('expires at'),
        help_text=_('When the invitation expires')
    )
    
    accepted = models.BooleanField(
        _('accepted'),
        default=False,
        help_text=_('Whether the invitation was accepted')
    )
    
    rejected = models.BooleanField(
        _('rejected'),
        default=False,
        help_text=_('Whether the invitation was rejected')
    )
    
    message = models.TextField(
        _('message'),
        blank=True,
        null=True,
        help_text=_('Optional message to the invitee')
    )
    
    class Meta:
        verbose_name = _('team invite')
        verbose_name_plural = _('team invites')
        unique_together = ['team', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team.name} invited {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Set default expiration time if not provided."""
        if not self.expires_at:
            # Default to 7 days from now
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the invitation has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_pending(self):
        """Check if the invitation is pending (not accepted, rejected, or expired)."""
        return not (self.accepted or self.rejected or self.is_expired)
    
    def accept(self):
        """Accept the invitation and add the user to the team."""
        if not self.is_pending:
            raise ValueError(_("Invitation cannot be accepted (already processed or expired)"))
        
        if self.team.is_full:
            raise ValueError(_("Team is already at maximum capacity"))
        
        if self.user.team:
            raise ValueError(_("User is already in a team"))
        
        # Add user to the team
        self.user.team = self.team
        self.user.save(update_fields=['team'])
        
        # Update invitation status
        self.accepted = True
        self.save(update_fields=['accepted'])
        
        # Create log entry
        TeamMembershipLog.objects.create(
            team=self.team,
            user=self.user,
            action='join_via_invite'
        )
        
        return True
    
    def reject(self):
        """Reject the invitation."""
        if not self.is_pending:
            raise ValueError(_("Invitation cannot be rejected (already processed or expired)"))
        
        # Update invitation status
        self.rejected = True
        self.save(update_fields=['rejected'])
        
        return True


class TeamMembershipLog(models.Model):
    """
    Model for logging team membership changes.
    """
    ACTION_CHOICES = [
        ('join', _('Joined team')),
        ('leave', _('Left team')),
        ('kick', _('Kicked from team')),
        ('join_via_invite', _('Joined via invitation')),
        ('join_via_code', _('Joined via invite code')),
        ('join_via_password', _('Joined via password')),
        ('captain_change', _('Captain changed')),
        ('team_disbanded', _('Team disbanded')),
        ('request_approved', _('Join request approved')),
        ('request_rejected', _('Join request rejected'))
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='membership_logs',
        help_text=_('Team involved')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_membership_logs',
        help_text=_('User involved')
    )
    
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=ACTION_CHOICES,
        help_text=_('Action performed')
    )
    
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='performed_team_actions',
        null=True,
        blank=True,
        help_text=_('User who performed the action (if applicable)')
    )
    
    timestamp = models.DateTimeField(
        _('timestamp'),
        default=timezone.now,
        help_text=_('When the action occurred')
    )
    
    note = models.TextField(
        _('note'),
        blank=True,
        null=True,
        help_text=_('Additional information about the action')
    )
    
    class Meta:
        verbose_name = _('team membership log')
        verbose_name_plural = _('team membership logs')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.team.name}"


class TeamChallengeSolve(models.Model):
    """
    Model to track challenge solves by teams.
    """
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='team_solves',
        help_text=_('Team that solved the challenge')
    )
    
    challenge = models.ForeignKey(
        'challenges.Challenge',
        on_delete=models.CASCADE,
        related_name='team_solves',
        help_text=_('Challenge that was solved')
    )
    
    solved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='team_solves',
        null=True,
        blank=True,
        help_text=_('Team member who submitted the correct flag')
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
        verbose_name = _('team challenge solve')
        verbose_name_plural = _('team challenge solves')
        ordering = ['-timestamp']
        unique_together = ['team', 'challenge']
    
    def __str__(self):
        return f"{self.team.name} solved {self.challenge.name}"
    
    def save(self, *args, **kwargs):
        """Override save to update team score."""
        # Update first_blood if this is the first solve
        if not TeamChallengeSolve.objects.filter(challenge=self.challenge).exists():
            self.first_blood = True
            
        super().save(*args, **kwargs)
        
        # Update team score if this is a new solve
        if kwargs.get('created', True):
            self.team.increment_score(self.points)


class TeamSettings(models.Model):
    """
    Model for team-specific settings.
    """
    team = models.OneToOneField(
        Team,
        on_delete=models.CASCADE,
        related_name='team_settings',
        help_text=_('Team these settings belong to')
    )
    
    auto_accept_members = models.BooleanField(
        _('auto-accept members'),
        default=False,
        help_text=_('Automatically accept join requests')
    )
    
    require_captain_approval = models.BooleanField(
        _('require captain approval'),
        default=True,
        help_text=_('Require captain approval for new members')
    )
    
    allow_member_invites = models.BooleanField(
        _('allow member invites'),
        default=False,
        help_text=_('Allow regular members to invite new members')
    )
    
    share_solves_with_members = models.BooleanField(
        _('share solves with members'),
        default=True,
        help_text=_('Share challenge solutions with all team members')
    )
    
    leaderboard_visibility = models.BooleanField(
        _('leaderboard visibility'),
        default=True,
        help_text=_('Show team on public leaderboards')
    )
    
    max_members = models.IntegerField(
        _('maximum members'),
        default=5,
        help_text=_('Maximum number of members allowed in the team')
    )
    
    class Meta:
        verbose_name = _('team settings')
        verbose_name_plural = _('team settings')
    
    def __str__(self):
        return f"Settings for {self.team.name}"


class TeamJoinRequest(models.Model):
    """
    Model for tracking requests to join a team.
    """
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='join_requests',
        help_text=_('Team the user wants to join')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_join_requests',
        help_text=_('User requesting to join')
    )
    
    message = models.TextField(
        _('message'),
        blank=True,
        null=True,
        help_text=_('Optional message to team captain')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        default=timezone.now,
        help_text=_('When the request was created')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=[
            ('pending', _('Pending')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected'))
        ],
        default='pending',
        help_text=_('Current status of the request')
    )
    
    class Meta:
        verbose_name = _('team join request')
        verbose_name_plural = _('team join requests')
        unique_together = ['team', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} requests to join {self.team.name}"
    
    def approve(self, approver=None):
        """Approve the join request."""
        if self.status != 'pending':
            raise ValueError(_("This request has already been processed"))
        
        # Check if team is full
        if self.team.is_full:
            self.status = 'rejected'
            self.save(update_fields=['status'])
            raise ValueError(_("Team is already at maximum capacity"))
        
        # Check if user is already in a team
        if self.user.team:
            self.status = 'rejected'
            self.save(update_fields=['status'])
            raise ValueError(_("User is already in a team"))
        
        # Add user to team
        self.user.team = self.team
        self.user.save(update_fields=['team'])
        
        # Update request status
        self.status = 'approved'
        self.save(update_fields=['status'])
        
        # Create log entry
        TeamMembershipLog.objects.create(
            team=self.team,
            user=self.user,
            action='request_approved',
            performed_by=approver
        )
        
        return True
    
    def reject(self, rejecter=None):
        """Reject the join request."""
        if self.status != 'pending':
            raise ValueError(_("This request has already been processed"))
        
        # Update request status
        self.status = 'rejected'
        self.save(update_fields=['status'])
        
        # Create log entry
        TeamMembershipLog.objects.create(
            team=self.team,
            user=self.user,
            action='request_rejected',
            performed_by=rejecter
        )
        
        return True
