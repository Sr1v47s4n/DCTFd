"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import template
import os

register = template.Library()

@register.filter
def endswith(value, arg):
    """
    Returns True if the value ends with the argument.
    """
    return value.endswith(arg)

@register.filter(name='file_extension')
def file_extension(filename):
    """
    Returns the file extension.
    """
    if not filename:
        return ""
    parts = filename.split('.')
    if len(parts) > 1:
        return parts[-1].lower()
    return ""

@register.filter(name='get_filename')
def get_filename(filepath):
    """
    Returns just the filename from a path.
    """
    return os.path.basename(filepath) if filepath else ""


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key.
    """
    if not dictionary or key is None:
        return None
    return dictionary.get(key)
