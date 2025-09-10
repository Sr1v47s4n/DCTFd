"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import BaseUser
from .avatar_models import AvatarCategory, AvatarOption
from utils.country_code import COUNTRY_CHOICES
from core.form_mixins import CustomFieldFormMixin


class UserRegistrationForm(CustomFieldFormMixin, UserCreationForm):
    """
    Form for user registration with custom fields
    """
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )

    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )

    last_name = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )

    phone = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    country = forms.ChoiceField(
        label=_("Country"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=BaseUser.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    avatar = forms.ModelChoiceField(
        label=_("Choose an Avatar"),
        queryset=AvatarOption.objects.all(),
        required=False,
        widget=forms.RadioSelect(attrs={"class": "avatar-selection-widget"}),
    )

    class Meta:
        model = BaseUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "country",
            "gender",
            "avatar",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group avatar options by category for better organization in the form
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


class UserLoginForm(AuthenticationForm):
    """
    Form for user login with styled widgets
    """
    username = forms.CharField(
        label=_("Email or Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email or Username'})
    )
    
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    email = forms.EmailField(
        label=_("Email"),
        disabled=True,  # Email cannot be changed
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    username = forms.CharField(
        label=_("Username"),
        disabled=True,  # Username cannot be changed
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    last_name = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+1XXXXXXXXXX (must have 9-15 digits)",
            }
        ),
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message=_(
                    "Enter a valid phone number (e.g., +1234567890). Must have 9-15 digits."
                ),
                flags=0,
            )
        ],
        help_text=_(
            "Enter a phone number starting with + followed by country code and number. Must be 9-15 digits total."
        ),
    )

    country = forms.ChoiceField(
        label=_("Country"),
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    gender = forms.ChoiceField(
        label=_("Gender"),
        choices=BaseUser.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    bio = forms.CharField(
        label=_("Biography"),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    affiliation = forms.CharField(
        label=_("Affiliation"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    website = forms.URLField(
        label=_("Website"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    # Social media fields
    discord_id = forms.CharField(
        label=_("Discord ID"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    github_username = forms.CharField(
        label=_("GitHub Username"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    linkedin_profile = forms.URLField(
        label=_("LinkedIn Profile"),
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    twitter_username = forms.CharField(
        label=_("Twitter Username"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    avatar = forms.ModelChoiceField(
        label=_("Profile Avatar"),
        queryset=AvatarOption.objects.all(),
        required=False,
        widget=forms.RadioSelect(attrs={"class": "avatar-selection-widget"}),
        help_text=_("Select your preferred avatar image"),
    )

    custom_avatar = forms.ImageField(
        label=_("Custom Profile Picture (Legacy)"),
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
        help_text=_("We recommend selecting from our predefined avatars instead."),
    )

    hidden = forms.BooleanField(
        label=_("Hide profile from public listings"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = BaseUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "country",
            "gender",
            "bio",
            "affiliation",
            "website",
            "discord_id",
            "github_username",
            "linkedin_profile",
            "twitter_username",
            "avatar",
            "custom_avatar",
            "hidden",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Group avatar options by category for better organization in the form
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

    def clean_avatar(self):
        """
        Add custom validation and processing for the avatar field
        """
        avatar = self.cleaned_data.get("avatar")
        print(f"[DEBUG-FORM] clean_avatar called. Cleaned data avatar: {avatar}")

        # If avatar ID is provided as a string, convert it to AvatarOption object
        if avatar and isinstance(avatar, str) and avatar.isdigit():
            print(f"[DEBUG-FORM] Converting avatar ID string to AvatarOption")
            try:
                avatar = AvatarOption.objects.get(id=int(avatar))
                print(f"[DEBUG-FORM] Found avatar: {avatar}")
            except AvatarOption.DoesNotExist:
                print(f"[DEBUG-FORM] Avatar not found for ID: {avatar}")
                raise forms.ValidationError("Selected avatar does not exist")

        return avatar


class PasswordResetRequestForm(PasswordResetForm):
    """
    Form for requesting a password reset with styled widgets
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )


class CustomSetPasswordForm(SetPasswordForm):
    """
    Form for setting a new password with styled widgets
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
    )
    
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )
