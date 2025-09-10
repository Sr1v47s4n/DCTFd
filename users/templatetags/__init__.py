"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django import template
from django.utils.safestring import mark_safe
from users.avatar_models import AvatarCategory

register = template.Library()

@register.simple_tag
def render_avatar_selection(field):
    """
    Custom template tag to render the avatar selection widget
    """
    html = ['<div class="avatar-options-container">']
    
    # Group by category
    for group_name, options in field.field.choices:
        # Start category section
        html.append(f'<div class="avatar-category"><div class="avatar-category-title">{group_name}</div>')
        html.append('<div class="avatar-options">')
        
        # Render options in this category
        for value, option in options:
            checked = 'checked' if str(field.value()) == str(value) else ''
            selected_class = 'selected' if str(field.value()) == str(value) else ''
            
            html.append(f'''
            <div class="avatar-option {selected_class}">
                <input type="radio" name="{field.html_name}" value="{value}" id="avatar_{value}" 
                       class="avatar-radio" {checked}>
                <img src="{option.image.url}" alt="{option.name}" title="{option.name}">
                <div class="avatar-check-icon">
                    <i class="fas fa-check"></i>
                </div>
            </div>
            ''')
        
        # End category section
        html.append('</div></div>')
    
    html.append('</div>')
    return mark_safe('\n'.join(html))
