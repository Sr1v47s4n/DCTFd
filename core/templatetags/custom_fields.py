"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_custom_field_value(data, field_id):
    """Get the value of a custom field from the form data"""
    if str(field_id) in data:
        return data[str(field_id)]
    return ""

@register.filter
def get_custom_field_values(data, field_id):
    """Get the values of a multi-value custom field from the form data"""
    if str(field_id) in data:
        value = data[str(field_id)]
        if isinstance(value, list):
            return value
        try:
            # Try to parse as JSON list
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, return as a single-item list
            return [value]
    return []

@register.filter
def get_custom_field_error(errors, field_id):
    """Get the error message for a custom field"""
    if str(field_id) in errors:
        return errors[str(field_id)]
    return ""

@register.filter
def render_custom_field_value(field, value):
    """Render the value of a custom field appropriately based on field type"""
    if not value:
        return "-"
    
    field_type = field.field_type
    
    if field_type == 'checkbox':
        # For checkbox fields, value might be a list
        if isinstance(value, list):
            return mark_safe("<br>".join(value))
        try:
            # Try to parse as JSON list
            values = json.loads(value)
            return mark_safe("<br>".join(values))
        except (json.JSONDecodeError, TypeError):
            return value
    
    elif field_type == 'boolean':
        # For boolean fields, render Yes/No
        if value in [True, 1, '1', 'true', 'True', 'yes', 'Yes']:
            return "Yes"
        return "No"
    
    elif field_type == 'url':
        # For URL fields, make it a clickable link
        return mark_safe(f'<a href="{value}" target="_blank">{value}</a>')
    
    # Default: just return the value as is
    return value
