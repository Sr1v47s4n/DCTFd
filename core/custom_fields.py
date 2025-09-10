"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class CustomFieldDefinition(models.Model):
    """
    Definition of a custom field that can be used for various entities (users, teams, etc.)
    """
    FIELD_TYPE_CHOICES = [
        ('text', _('Text')),
        ('textarea', _('Text Area')),
        ('number', _('Number')),
        ('email', _('Email')),
        ('url', _('URL')),
        ('date', _('Date')),
        ('select', _('Dropdown')),
        ('radio', _('Radio Buttons')),
        ('checkbox', _('Checkboxes')),
        ('boolean', _('Yes/No Checkbox')),
    ]
    
    FIELD_FOR_CHOICES = [
        ('user', _('User')),
        ('team', _('Team')),
    ]
    
    # Generic relation to the related entity (typically Event)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='custom_field_definitions',
        verbose_name=_('content type')
    )
    object_id = models.PositiveIntegerField(_('object id'))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    field_for = models.CharField(
        _('field for'),
        max_length=20,
        choices=FIELD_FOR_CHOICES,
        help_text=_('Type of form this field is for')
    )
    
    field_type = models.CharField(
        _('field type'),
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        default='text',
        help_text=_('Type of the custom field')
    )
    
    label = models.CharField(
        _('field label'),
        max_length=255,
        help_text=_('Label to display to users')
    )
    
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Description or help text for the field')
    )
    
    placeholder = models.CharField(
        _('placeholder'),
        max_length=255,
        blank=True,
        help_text=_('Placeholder text for text fields')
    )
    
    options = models.TextField(
        _('options'),
        blank=True,
        help_text=_('Options for select/radio/checkbox fields (one per line)')
    )
    
    required = models.BooleanField(
        _('required'),
        default=False,
        help_text=_('Whether this field is required')
    )
    
    order = models.PositiveIntegerField(
        _('display order'),
        default=0,
        help_text=_('Order in which to display the field')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    
    class Meta:
        ordering = ['field_for', 'order']
        verbose_name = _('Custom Field Definition')
        verbose_name_plural = _('Custom Field Definitions')
    
    def __str__(self):
        return f"{self.label} ({self.get_field_for_display()})"
    
    def get_options_list(self):
        """Returns the options as a list for select/radio/checkbox fields"""
        if not self.options:
            return []
        return [option.strip() for option in self.options.split('\n') if option.strip()]


class CustomFieldValue(models.Model):
    """
    Value for a custom field for a specific entity instance
    """
    field_definition = models.ForeignKey(
        CustomFieldDefinition,
        on_delete=models.CASCADE,
        related_name='values',
        help_text=_('The custom field this value is for')
    )
    
    # Generic relation to the entity (user or team)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    value = models.TextField(
        _('field value'),
        blank=True,
        help_text=_('Value for this custom field')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Custom Field Value')
        verbose_name_plural = _('Custom Field Values')
        unique_together = ['field_definition', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.field_definition.label}: {self.value}"
