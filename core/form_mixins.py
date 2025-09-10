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
from users.models import BaseUser

class CustomFieldFormMixin:
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.field_for = kwargs.pop('field_for', None)
        self.instance = kwargs.get('instance', None)
        
        super().__init__(*args, **kwargs)
        
        if self.event and self.field_for:
            self.add_custom_fields()
    
    def add_custom_fields(self):
        # Get content type for event
        event_content_type = ContentType.objects.get_for_model(Event)
        
        # Get custom field definitions for this event and field_for
        custom_fields = CustomFieldDefinition.objects.filter(
            content_type=event_content_type,
            object_id=self.event.id,
            field_for=self.field_for
        ).order_by('order')
        
        # Add each custom field to the form
        for field_def in custom_fields:
            field_name = f"custom_field_{field_def.id}"
            
            # Create the appropriate form field based on the field type
            if field_def.field_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.TextInput(attrs={'placeholder': field_def.placeholder})
                )
            elif field_def.field_type == 'textarea':
                self.fields[field_name] = forms.CharField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.Textarea(attrs={'placeholder': field_def.placeholder, 'rows': 3})
                )
            elif field_def.field_type == 'email':
                self.fields[field_name] = forms.EmailField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.EmailInput(attrs={'placeholder': field_def.placeholder})
                )
            elif field_def.field_type == 'number':
                self.fields[field_name] = forms.IntegerField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.NumberInput(attrs={'placeholder': field_def.placeholder})
                )
            elif field_def.field_type == 'url':
                self.fields[field_name] = forms.URLField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.URLInput(attrs={'placeholder': field_def.placeholder})
                )
            elif field_def.field_type == 'date':
                self.fields[field_name] = forms.DateField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.DateInput(attrs={'type': 'date'})
                )
            elif field_def.field_type == 'select':
                choices = [(option.strip(), option.strip()) for option in field_def.options.split('\n') if option.strip()]
                self.fields[field_name] = forms.ChoiceField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    choices=[('', _('Select an option'))] + choices,
                    widget=forms.Select()
                )
            elif field_def.field_type == 'radio':
                choices = [(option.strip(), option.strip()) for option in field_def.options.split('\n') if option.strip()]
                self.fields[field_name] = forms.ChoiceField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    choices=choices,
                    widget=forms.RadioSelect()
                )
            elif field_def.field_type == 'checkbox':
                choices = [(option.strip(), option.strip()) for option in field_def.options.split('\n') if option.strip()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple()
                )
            elif field_def.field_type == 'boolean':
                self.fields[field_name] = forms.BooleanField(
                    label=field_def.label,
                    help_text=field_def.description,
                    required=field_def.required,
                    widget=forms.CheckboxInput()
                )
            
            # If we have an instance, populate with existing custom field value
            if self.instance and self.instance.pk:
                try:
                    field_value = CustomFieldValue.objects.get(
                        field_definition=field_def,
                        content_type=ContentType.objects.get_for_model(self.instance),
                        object_id=self.instance.pk
                    )
                    if field_def.field_type == 'checkbox':
                        self.initial[field_name] = field_value.value.split(',')
                    else:
                        self.initial[field_name] = field_value.value
                except CustomFieldValue.DoesNotExist:
                    pass
    
    def save_custom_fields(self, obj):
        if not self.event or not self.field_for:
            return
        
        # Get content type for event and object
        event_content_type = ContentType.objects.get_for_model(Event)
        obj_content_type = ContentType.objects.get_for_model(obj)
        
        # Get custom field definitions for this event and field_for
        custom_fields = CustomFieldDefinition.objects.filter(
            content_type=event_content_type,
            object_id=self.event.id,
            field_for=self.field_for
        )
        
        # Save each custom field value
        for field_def in custom_fields:
            field_name = f"custom_field_{field_def.id}"
            
            if field_name in self.cleaned_data:
                field_value = self.cleaned_data[field_name]
                
                # Convert list values to comma-separated string
                if isinstance(field_value, list):
                    field_value = ','.join(field_value)
                
                # Save or update the custom field value
                if field_value or field_value == False:  # Save even if it's False (for boolean fields)
                    CustomFieldValue.objects.update_or_create(
                        field_definition=field_def,
                        content_type=obj_content_type,
                        object_id=obj.pk,
                        defaults={'value': str(field_value)}
                    )
                else:
                    # Delete the value if it's empty and not required
                    CustomFieldValue.objects.filter(
                        field_definition=field_def,
                        content_type=obj_content_type,
                        object_id=obj.pk
                    ).delete()
