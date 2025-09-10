"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """
    Get an attribute of an object dynamically from a string name
    """
    if hasattr(obj, attr):
        return getattr(obj, attr)
    
    # For form fields
    if hasattr(obj, 'fields') and attr in obj.fields:
        return obj[attr]
    
    return None

@register.filter
def field_errors(field):
    """
    Get errors for a field, supports both normal fields and bound fields
    """
    if isinstance(field, BoundField):
        return field.errors
    return None
