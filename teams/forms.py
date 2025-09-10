"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Team
from utils.country_code import COUNTRY_CHOICES
from core.form_mixins import CustomFieldFormMixin
from users.avatar_models import AvatarOption, AvatarCategory

class TeamCreationForm(CustomFieldFormMixin, forms.ModelForm):
    """
    Form for creating a new team with optional custom fields
    """
    name = forms.CharField(
        label=_("Team Name"),
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Team Name')})
    )

    password = forms.CharField(
        label=_("Team Password"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Optional Password to Join')}),
        help_text=_("Optional password required for others to join your team. Leave blank for invite-only.")
    )

    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Team Description')}),
        help_text=_("Tell others about your team")
    )

    country = forms.ChoiceField(
        label=_("Country"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    affiliation = forms.CharField(
        label=_("Affiliation"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('School, Company, or Organization')}),
    )

    logo = forms.ImageField(
        label=_("Team Logo (Legacy)"),
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
        help_text=_("We recommend selecting from our predefined avatars instead."),
    )

    avatar = forms.ModelChoiceField(
        label=_("Team Avatar"),
        queryset=AvatarOption.objects.all(),
        required=False,
        widget=forms.RadioSelect(attrs={"class": "avatar-selection-widget"}),
        help_text=_("Select your team's avatar image"),
    )

    class Meta:
        model = Team
        fields = [
            "name",
            "password",
            "description",
            "country",
            "affiliation",
            "logo",
            "avatar",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group avatar options by category for better organization
        avatar_choices = []
        categories = AvatarCategory.objects.prefetch_related("avatars").all()

        for category in categories:
            category_avatars = [
                (avatar.id, avatar) for avatar in category.avatars.all()
            ]
            if category_avatars:
                avatar_choices.append((category.name, category_avatars))

        if avatar_choices:
            self.fields["avatar"].choices = avatar_choices

        # If no avatar is selected, use the default
        if not self.initial.get("avatar"):
            default_avatar = AvatarOption.objects.filter(is_default=True).first()
            if default_avatar:
                self.initial["avatar"] = default_avatar.id

    def save(self, commit=True, **kwargs):
        instance = super().save(commit=False)

        # Auto-generate slug if needed
        if not instance.slug:
            from django.utils.text import slugify
            instance.slug = slugify(instance.name)

        if commit:
            instance.save()

            # Save custom fields if any
            if hasattr(self, 'save_custom_fields'):
                self.save_custom_fields(instance)

        return instance


class TeamJoinForm(forms.Form):
    """
    Form for joining an existing team
    """
    team = forms.ModelChoiceField(
        label=_("Team"),
        queryset=Team.objects.filter(status='active'),
        empty_label=_("Select a team"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label=_("Team Password"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Team Password (if required)')}),
        help_text=_("Leave blank if the team doesn't require a password")
    )

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super(TeamJoinForm, self).__init__(*args, **kwargs)

        if self.event:
            # Filter teams by event
            self.fields['team'].queryset = Team.objects.filter(
                status='active',
                event=self.event
            )


class TeamProfileUpdateForm(forms.ModelForm):
    """
    Form for updating a team's profile information
    """

    name = forms.CharField(
        label=_("Team Name"),
        disabled=True,  # Team name cannot be changed
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        help_text=_("Tell others about your team"),
    )

    country = forms.ChoiceField(
        label=_("Country"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    affiliation = forms.CharField(
        label=_("Affiliation"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text=_("School, company, or organization"),
    )

    website = forms.URLField(
        label=_("Website"),
        required=False,
        widget=forms.URLInput(attrs={"class": "form-control"}),
        help_text=_("Team website or blog"),
    )

    logo = forms.ImageField(
        label=_("Team Logo (Legacy)"),
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
        help_text=_("We recommend selecting from our predefined avatars instead."),
    )

    avatar = forms.ModelChoiceField(
        label=_("Team Avatar"),
        queryset=AvatarOption.objects.all(),
        required=False,
        widget=forms.RadioSelect(attrs={"class": "avatar-selection-widget"}),
        help_text=_("Select your team's avatar image"),
    )

    class Meta:
        model = Team
        fields = [
            "name",
            "description",
            "country",
            "affiliation",
            "website",
            "logo",
            "avatar",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group avatar options by category for better organization
        avatar_choices = []
        categories = AvatarCategory.objects.prefetch_related("avatars").all()

        for category in categories:
            category_avatars = [
                (avatar.id, avatar) for avatar in category.avatars.all()
            ]
            if category_avatars:
                avatar_choices.append((category.name, category_avatars))

        if avatar_choices:
            self.fields["avatar"].choices = avatar_choices
