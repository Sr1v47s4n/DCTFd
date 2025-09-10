"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get a dictionary item by its key.
    Usage: {{ mydict|get_item:item_key }}
    """
    return dictionary.get(key, '')

@register.filter
def progress_color(value):
    """
    Return bootstrap color class based on progress percentage.
    Usage: {{ percentage|progress_color }}
    """
    if value >= 75:
        return 'success'
    elif value >= 50:
        return 'info'
    elif value >= 25:
        return 'warning'
    else:
        return 'danger'
        
@register.filter
def status_badge(status):
    """
    Return bootstrap badge class based on status.
    Usage: {{ status|status_badge }}
    """
    status_classes = {
        'correct': 'success',
        'incorrect': 'danger',
        'pending': 'warning',
        'open': 'success',
        'closed': 'danger',
        'running': 'primary',
        'planning': 'secondary',
        'registration': 'info',
        'completed': 'dark',
    }
    return status_classes.get(status.lower(), 'secondary')

@register.filter
def shorten_text(text, length=50):
    """
    Shorten text to a specified length and add ellipsis if needed.
    Usage: {{ long_text|shorten_text:100 }}
    """
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length] + '...'
