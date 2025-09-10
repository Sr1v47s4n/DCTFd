"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from event.models import Event
from challenges.models import Challenge, ChallengeCategory, ChallengeFile, Flag, Hint


class EventForm(forms.ModelForm):
    """Form for managing CTF event settings"""
    
    class Meta:
        model = Event
        fields = ['name', 'description', 'short_description', 'logo', 'banner', 
                 'start_time', 'end_time', 'registration_start', 'registration_end',
                 'status', 'access', 'max_team_size', 'min_team_size',
                 'is_visible', 'scoreboard_visible', 'allow_individual_participants']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'My Awesome CTF'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your CTF event...'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description of your CTF'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'registration_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'access': forms.Select(attrs={'class': 'form-select'}),
            'max_team_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'min_team_size': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scoreboard_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_individual_participants': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        reg_start = cleaned_data.get('registration_start')
        reg_end = cleaned_data.get('registration_end')
        
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError(_('End time must be after start time.'))
            
        if reg_start and reg_end and reg_end <= reg_start:
            raise forms.ValidationError(_('Registration end time must be after registration start time.'))
            
        if reg_end and start_time and reg_end > start_time:
            raise forms.ValidationError(_('Registration should end before the event starts.'))
            
        return cleaned_data


class ChallengeForm(forms.ModelForm):
    """Form for creating and editing challenges"""

    prerequisites = forms.ModelMultipleChoiceField(
        queryset=Challenge.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select select2",
                "data-placeholder": "Select prerequisite challenges...",
            }
        ),
        help_text=_("Challenges that must be solved before this one becomes visible"),
    )

    class Meta:
        model = Challenge
        fields = [
            "name",
            "description",
            "category",
            "value",
            "initial_value",
            "min_value",
            "decay",
            "decay_threshold",
            "difficulty",
            "max_attempts",
            "is_visible",
            "type",
            "flag_logic",
            "state",
            "prerequisites",
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Challenge Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6, 
                'placeholder': 'Challenge description... (supports markdown)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'placeholder': 'Points (e.g., 500)'
            }),
            'initial_value': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'placeholder': 'Initial points for dynamic scoring'
            }),
            'min_value': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1, 
                'placeholder': 'Minimum points'
            }),
            'decay': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Decay factor (0.01 - 1.0)'
            }),
            'decay_threshold': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 1,
                'placeholder': 'Solves before decay starts'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'max_attempts': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'placeholder': 'Max attempts (0 = unlimited)'
            }),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'flag_logic': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data.get('value')
        initial_value = cleaned_data.get('initial_value')
        min_value = cleaned_data.get('min_value')
        decay = cleaned_data.get('decay')

        # Validate scoring values
        if initial_value and min_value and initial_value <= min_value:
            raise forms.ValidationError(_('Initial value must be greater than minimum value.'))

        if value and min_value and value < min_value:
            raise forms.ValidationError(_('Value must be greater than or equal to minimum value.'))

        if decay and (decay < 0.01 or decay > 1.0):
            raise forms.ValidationError(_('Decay factor must be between 0.01 and 1.0.'))

        return cleaned_data


class FlagForm(forms.ModelForm):
    """Form for adding flags to challenges"""
    
    class Meta:
        model = Flag
        fields = ['flag', 'type']
        
        widgets = {
            'flag': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Flag content (e.g., CTF{flag_here})'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }


class HintForm(forms.ModelForm):
    """Form for adding hints to challenges"""
    
    class Meta:
        model = Hint
        fields = ['content', 'cost']
        
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Hint content...'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0,
                'placeholder': 'Cost in points'
            }),
        }


class ChallengeFileForm(forms.ModelForm):
    """Form for uploading challenge files"""
    
    class Meta:
        model = ChallengeFile
        fields = ['file', 'name']
        
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'File display name (optional)'
            }),
        }
