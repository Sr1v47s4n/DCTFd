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
import uuid
import os


def challenge_file_path(instance, filename):
    """Generate unique path for challenge files."""
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('challenges', str(instance.challenge.id), unique_filename)


def solution_file_path(instance, filename):
    """Generate unique path for solution files."""
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('solutions', str(instance.solution.id), unique_filename)


def file_upload_path(instance, filename):
    """Generate unique path for challenge files."""
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('files', str(instance.challenge.id), unique_filename)


class ChallengeCategory(models.Model):
    """
    Model for categorizing challenges.
    """
    name = models.CharField(
        _('name'),
        max_length=80,
        unique=True,
        help_text=_('Category name')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Category description')
    )

    icon = models.CharField(
        _('icon'),
        max_length=30,
        blank=True,
        null=True,
        help_text=_('FontAwesome icon class')
    )

    color = models.CharField(
        _('color'),
        max_length=20,
        default='#007bff',
        help_text=_('HEX color code for this category')
    )

    order = models.IntegerField(
        _('order'),
        default=0,
        help_text=_('Display order of the category')
    )

    is_hidden = models.BooleanField(
        _("hidden"), default=False, help_text=_("Whether the category is hidden")
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the category was created')
    )

    class Meta:
        verbose_name = _('challenge category')
        verbose_name_plural = _('challenge categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Challenge(models.Model):
    """
    Model for CTF challenges.
    """
    STATE_CHOICES = [
        ('hidden', _('Hidden')),
        ('visible', _('Visible')),
        ('locked', _('Locked'))
    ]

    TYPE_CHOICES = [
        ('standard', _('Standard')),
        ('dynamic', _('Dynamic')),
        ('scripted', _('Scripted'))
    ]

    LOGIC_CHOICES = [
        ('any', _('Any Flag')),
        ('all', _('All Flags'))
    ]

    name = models.CharField(
        _('name'),
        max_length=80,
        help_text=_('Challenge name')
    )

    description = models.TextField(
        _('description'),
        help_text=_('Challenge description')
    )

    category = models.ForeignKey(
        ChallengeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='challenges',
        help_text=_('Challenge category')
    )

    value = models.IntegerField(
        _('value'),
        default=100,
        help_text=_('Challenge point value')
    )

    initial_value = models.IntegerField(
        _('initial value'),
        default=100,
        help_text=_('Initial challenge point value for dynamic scoring')
    )

    min_value = models.IntegerField(
        _('minimum value'),
        default=50,
        help_text=_('Minimum challenge point value for dynamic scoring')
    )

    decay = models.FloatField(
        _('decay'),
        default=0.0,
        help_text=_('Score decay factor for dynamic scoring')
    )

    decay_threshold = models.IntegerField(
        _('decay threshold'),
        default=1,
        help_text=_('Number of solves before decay starts')
    )

    max_attempts = models.IntegerField(
        _('max attempts'),
        default=0,
        help_text=_('Maximum number of attempts allowed (0 for unlimited)')
    )

    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='standard',
        help_text=_('Challenge type')
    )

    state = models.CharField(
        _('state'),
        max_length=20,
        choices=STATE_CHOICES,
        default='visible',
        help_text=_('Challenge visibility state')
    )

    is_visible = models.BooleanField(
        _('is visible'),
        default=True,
        help_text=_('Whether this challenge is visible to users')
    )

    flag_logic = models.CharField(
        _('flag logic'),
        max_length=10,
        choices=LOGIC_CHOICES,
        default='any',
        help_text=_('Logic for determining if multiple flags are correct')
    )

    author = models.CharField(
        _('author'),
        max_length=80,
        blank=True,
        null=True,
        help_text=_('Challenge author name')
    )

    difficulty = models.IntegerField(
        _('difficulty'),
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Challenge difficulty (1-5)')
    )

    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='unlocks',
        help_text=_('Challenges that must be solved before this one is visible')
    )

    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        related_name='challenges',
        help_text=_('Event this challenge belongs to')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the challenge was created')
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the challenge was last updated')
    )

    class Meta:
        verbose_name = _('challenge')
        verbose_name_plural = _('challenges')
        ordering = ['category__order', 'value']

    def __str__(self):
        return self.name

    def check_flag(self, flag_str):
        """
        Check if the submitted flag is correct for this challenge.
        
        Returns (is_correct, matching_flag_or_none)
        """
        # Get all flags for this challenge
        flags = self.flags.all()

        if not flags.exists():
            return False, None

        # Check each flag
        for flag in flags:
            if flag.check_flag(flag_str):
                return True, flag

        return False, None

    def check_prerequisites_met(self, user):
        """
        Check if all prerequisites for this challenge have been met by the user or their team.

        Returns: Boolean indicating whether all prerequisites have been completed
        """
        # If no prerequisites, return True
        if not self.prerequisites.exists():
            return True

        # Get user's team if they have one
        team = getattr(user, "team", None)

        # Check if user/team has solved each prerequisite challenge
        for prerequisite in self.prerequisites.all():
            if team:
                prerequisite_solved = Submission.objects.filter(
                    team=team, challenge=prerequisite, is_correct=True
                ).exists()
            else:
                prerequisite_solved = Submission.objects.filter(
                    user=user, challenge=prerequisite, is_correct=True
                ).exists()

            if not prerequisite_solved:
                return False

        return True


class Flag(models.Model):
    """
    Model for challenge flags.
    """
    FLAG_TYPES = [
        ('static', _('Static')),
        ('regex', _('Regular Expression')),
        ('dynamic', _('Dynamic'))
    ]
    
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='flags',
        help_text=_('Related challenge')
    )
    
    flag = models.CharField(
        _('flag'),
        max_length=255,
        default='',
        help_text=_('Flag content or pattern')
    )
    
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=FLAG_TYPES,
        default='static',
        help_text=_('Flag type')
    )
    
    data = models.TextField(
        _('data'),
        blank=True,
        null=True,
        help_text=_('Additional data for dynamic flags')
    )
    
    is_case_insensitive = models.BooleanField(
        _('case insensitive'),
        default=False,
        help_text=_('Whether the flag is case insensitive')
    )
    
    class Meta:
        verbose_name = _('flag')
        verbose_name_plural = _('flags')
    
    def __str__(self):
        return f"Flag for {self.challenge.name}"
    
    def check_flag(self, flag_str):
        """
        Check if the submitted flag matches this flag.
        """
        import re
        
        # Handle case sensitivity
        if self.is_case_insensitive:
            flag_str = flag_str.lower()
            flag_content = self.flag.lower()
        else:
            flag_content = self.flag
        
        # Check based on flag type
        if self.type == 'static':
            return flag_str == flag_content
        elif self.type == 'regex':
            try:
                pattern = re.compile(flag_content)
                return bool(pattern.match(flag_str))
            except re.error:
                return False
        elif self.type == 'dynamic':
            # Dynamic flags would have custom logic here
            return False
        
        return False


class Submission(models.Model):
    """
    Model for tracking flag submissions.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text=_('Challenge the flag was submitted for')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text=_('User who submitted the flag')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submissions',
        help_text=_('Team the user belonged to at time of submission')
    )
    
    flag_submitted = models.CharField(
        _('flag submitted'),
        max_length=255,
        default='',
        help_text=_('The flag string that was submitted')
    )
    
    is_correct = models.BooleanField(
        _('is correct'),
        default=False,
        help_text=_('Whether the submission was correct')
    )
    
    submitted_at = models.DateTimeField(
        _('submitted at'),
        default=timezone.now,
        help_text=_('When the flag was submitted')
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        blank=True,
        null=True,
        help_text=_('IP address the submission came from')
    )
    
    class Meta:
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{'Correct' if self.is_correct else 'Incorrect'} submission for {self.challenge.name} by {self.user.username}"


class Hint(models.Model):
    """
    Model for challenge hints.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='hints',
        help_text=_('Related challenge')
    )
    
    content = models.TextField(
        _('content'),
        help_text=_('Hint content')
    )
    
    cost = models.IntegerField(
        _('cost'),
        default=0,
        help_text=_('Point cost to unlock this hint (0 for free)')
    )
    
    position = models.IntegerField(
        _('position'),
        default=0,
        help_text=_('Display order of the hint')
    )
    
    is_visible = models.BooleanField(
        _('is visible'),
        default=True,
        help_text=_('Whether this hint is visible to users')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the hint was created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the hint was last updated')
    )
    
    class Meta:
        verbose_name = _('hint')
        verbose_name_plural = _('hints')
        ordering = ['position']
    
    def __str__(self):
        return f"Hint for {self.challenge.name}"


class HintUnlock(models.Model):
    """
    Model for tracking hint unlocks by users.
    """
    hint = models.ForeignKey(
        Hint,
        on_delete=models.CASCADE,
        related_name='unlocks',
        help_text=_('Hint that was unlocked')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hint_unlocks',
        help_text=_('User who unlocked the hint')
    )
    
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hint_unlocks',
        help_text=_('Team the user belonged to when unlocking')
    )
    
    cost = models.IntegerField(
        _('cost'),
        default=0,
        help_text=_('Points deducted for unlocking this hint')
    )
    
    unlocked_at = models.DateTimeField(
        _('unlocked at'),
        default=timezone.now,
        help_text=_('When the hint was unlocked')
    )
    
    class Meta:
        verbose_name = _('hint unlock')
        verbose_name_plural = _('hint unlocks')
        unique_together = ['hint', 'user']
    
    def __str__(self):
        return f"{self.user.username} unlocked hint for {self.hint.challenge.name}"


class ChallengeFile(models.Model):
    """
    Model for challenge files.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='challenge_files',
        help_text=_('Related challenge')
    )
    
    file = models.FileField(
        _('file'),
        upload_to=challenge_file_path,
        help_text=_('Challenge file')
    )
    
    name = models.CharField(
        _('name'),
        max_length=255,
        help_text=_('Display name for the file')
    )
    
    description = models.CharField(
        _('description'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('File description')
    )
    
    size = models.PositiveIntegerField(
        _('size'),
        default=0,
        help_text=_('File size in bytes')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the file was uploaded')
    )
    
    class Meta:
        verbose_name = _('challenge file')
        verbose_name_plural = _('challenge files')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Set the file size on save
        if self.file and not self.size:
            self.size = self.file.size
            
        super().save(*args, **kwargs)


class File(models.Model):
    """
    Model for challenge files.
    """
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='file_uploads',
        help_text=_('Related challenge')
    )

    file = models.FileField(
        _('file'),
        upload_to=file_upload_path,
        help_text=_('Challenge file')
    )

    filename = models.CharField(
        _('filename'),
        max_length=255,
        help_text=_('Original filename')
    )

    description = models.CharField(
        _('description'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('File description')
    )

    size = models.PositiveIntegerField(
        _('size'),
        default=0,
        help_text=_('File size in bytes')
    )

    is_visible = models.BooleanField(
        _('is visible'),
        default=True,
        help_text=_('Whether this file is visible to users')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the file was uploaded')
    )

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        # Set the file size on save
        if self.file and not self.size:
            self.size = self.file.size

        # Set the filename from the uploaded file if not specified
        if self.file and not self.filename:
            self.filename = os.path.basename(self.file.name)


class Comment(models.Model):
    """
    Model for challenge comments.
    """

    challenge = models.ForeignKey(
        "Challenge",
        on_delete=models.CASCADE,
        related_name="comments",
        help_text=_("The challenge this comment is associated with"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="challenge_comments",
        help_text=_("User who created the comment"),
    )

    content = models.TextField(_("content"), help_text=_("Comment content"))

    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, help_text=_("When the comment was created")
    )

    updated_at = models.DateTimeField(
        _("updated at"), auto_now=True, help_text=_("When the comment was last updated")
    )

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on Challenge #{self.challenge.id}"
        super().save(*args, **kwargs)
