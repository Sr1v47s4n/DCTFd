"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from core.custom_fields import CustomFieldDefinition, CustomFieldValue
from event.models import Event
from challenges.models import Challenge, Flag, ChallengeFile, ChallengeCategory


class CustomFieldDefinitionForm(forms.ModelForm):
    """Form for creating and editing custom field definitions"""

    class Meta:
        model = CustomFieldDefinition
        fields = [
            'field_for', 'field_type', 'label', 'description', 'placeholder', 
            'options', 'required', 'order'
        ]
        widgets = {
            'field_for': forms.Select(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'placeholder': forms.TextInput(attrs={'class': 'form-control'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'One option per line'}),
            'required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add hidden fields for content type and object id
        self.fields['content_type'] = forms.ModelChoiceField(
            queryset=ContentType.objects.filter(model='event'),
            widget=forms.HiddenInput(),
            required=False
        )

        self.fields['object_id'] = forms.IntegerField(
            widget=forms.HiddenInput(),
            required=False
        )

        # Set initial values for event content type and the active event
        if not self.instance.pk:
            try:
                event_content_type = ContentType.objects.get(app_label='event', model='event')
                self.fields['content_type'].initial = event_content_type.id

                # Try to get the active event
                active_event = Event.objects.filter(status__in=['registration', 'running']).first()
                if active_event:
                    self.fields['object_id'].initial = active_event.id
            except (ContentType.DoesNotExist, Event.DoesNotExist):
                pass

    def clean_label(self):
        label = self.cleaned_data.get('label')
        # Basic validation for label
        if not label:
            raise forms.ValidationError(_('Label is required'))
        return label

    def clean(self):
        cleaned_data = super().clean()
        field_type = cleaned_data.get('field_type')
        options = cleaned_data.get('options')

        # Validate that options are provided for select and radio fields
        if field_type in ['select', 'radio'] and not options:
            self.add_error('options', 'Options are required for select and radio field types')

        return cleaned_data


class ChallengeForm(forms.ModelForm):
    """Form for creating and editing challenges."""

    class Meta:
        model = Challenge
        fields = [
            "name",
            "description",
            "category",
            "value",
            "difficulty",
            "state",
            "is_visible",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "value": forms.NumberInput(attrs={"class": "form-control"}),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "state": forms.Select(attrs={"class": "form-select"}),
            "is_visible": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class FlagForm(forms.ModelForm):
    """Form for challenge flags."""

    class Meta:
        model = Flag
        fields = ["flag", "type", "data", "is_case_insensitive"]
        widgets = {
            "flag": forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-select"}),
            "data": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "is_case_insensitive": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


class ChallengeFileForm(forms.ModelForm):
    """Form for challenge files."""

    class Meta:
        model = ChallengeFile
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class ChallengeCategoryForm(forms.ModelForm):
    """Form for creating and editing challenge categories."""

    class Meta:
        model = ChallengeCategory
        fields = ["name", "description", "icon", "color", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "icon": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control", "type": "color"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
