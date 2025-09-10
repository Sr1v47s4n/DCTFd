"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import os
import uuid


def avatar_file_path(instance, filename):
    """Generate a unique path for avatar images."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('avatars', instance.category.slug, filename)


class AvatarCategory(models.Model):
    """
    Categories for avatars (tech, users, males, females, pets, cartoons, etc.)
    """
    name = models.CharField(_('name'), max_length=50, unique=True)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    display_order = models.PositiveSmallIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('Avatar Category')
        verbose_name_plural = _('Avatar Categories')
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class AvatarOption(models.Model):
    """
    Predefined avatar options for users to choose from
    """
    name = models.CharField(_('name'), max_length=100)
    category = models.ForeignKey(
        AvatarCategory, 
        on_delete=models.CASCADE,
        related_name='avatars',
        verbose_name=_('category')
    )
    image = models.ImageField(_('image'), upload_to=avatar_file_path)
    is_default = models.BooleanField(_('is default'), default=False)
    display_order = models.PositiveSmallIntegerField(_('display order'), default=0)
    
    class Meta:
        verbose_name = _('Avatar Option')
        verbose_name_plural = _('Avatar Options')
        ordering = ['category', 'display_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_per_category'
            )
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default avatar per category
        if self.is_default:
            AvatarOption.objects.filter(
                category=self.category, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
