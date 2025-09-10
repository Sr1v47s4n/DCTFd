"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .avatar_models import AvatarCategory, AvatarOption

@admin.register(AvatarCategory)
class AvatarCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('display_order', 'name')

@admin.register(AvatarOption)
class AvatarOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_default', 'display_order')
    list_filter = ('category', 'is_default')
    search_fields = ('name', 'category__name')
    ordering = ('category', 'display_order', 'name')
    list_editable = ('is_default', 'display_order')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'image')
        }),
        (_('Display Options'), {
            'fields': ('is_default', 'display_order')
        }),
    )
