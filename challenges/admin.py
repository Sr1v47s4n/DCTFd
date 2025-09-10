"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Challenge,
    ChallengeCategory,
    Flag,
    Hint,
    File,
    Submission,
    HintUnlock,
)

# Register your models here.


class FlagInline(admin.TabularInline):
    model = Flag
    extra = 1


class HintInline(admin.TabularInline):
    model = Hint
    extra = 1


class FileInline(admin.TabularInline):
    model = File
    extra = 1


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "value",
        "type",
        "state",
        "difficulty",
        "event",
        "created_at",
    )
    list_filter = ("category", "type", "state", "difficulty", "event")
    search_fields = ("name", "description", "author")
    filter_horizontal = ("prerequisites",)
    fieldsets = (
        (None, {"fields": ("name", "description", "category", "event")}),
        (
            _("Challenge Settings"),
            {
                "fields": (
                    "value",
                    "initial_value",
                    "min_value",
                    "decay",
                    "decay_threshold",
                    "max_attempts",
                    "type",
                    "state",
                    "is_visible",
                    "flag_logic",
                )
            },
        ),
        (_("Author & Difficulty"), {"fields": ("author", "difficulty")}),
        (
            _("Prerequisites"),
            {
                "fields": ("prerequisites",),
                "description": _(
                    "Select challenges that must be solved before this one becomes visible"
                ),
            },
        ),
    )
    inlines = [FlagInline, HintInline, FileInline]


@admin.register(ChallengeCategory)
class ChallengeCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "icon", "color", "order", "is_hidden")
    search_fields = ("name", "description")
    list_editable = ("order", "is_hidden")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("challenge", "user", "team", "is_correct", "submitted_at")
    list_filter = ("is_correct", "challenge", "submitted_at")
    search_fields = ("challenge__name", "user__username", "team__name")
    readonly_fields = ("submitted_at",)


@admin.register(HintUnlock)
class HintUnlockAdmin(admin.ModelAdmin):
    list_display = ("hint", "user", "team", "cost", "unlocked_at")
    list_filter = ("unlocked_at",)
    search_fields = ("hint__challenge__name", "user__username", "team__name")
