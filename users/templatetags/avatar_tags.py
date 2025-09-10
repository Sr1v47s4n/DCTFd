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
    Custom template tag to render the avatar selection widget with tabbed interface
    """
    # Start container
    html = ['<div class="avatar-selection-wrapper">']
    
    # Extract categories and options
    categories_data = []
    
    for group_name, options in field.field.choices:
        categories_data.append({
            'name': group_name,
            'options': options
        })
    
    # Create tabs for categories - we use a unique ID to ensure we can target these elements specifically
    html.append('<div class="avatar-category-tabs" id="avatar-selection-tabs">')
    
    for i, category in enumerate(categories_data):
        active_class = 'active' if i == 0 else ''
        html.append(f'<div class="avatar-category-tab {active_class}" data-category="{i}">{category["name"]}</div>')
    
    html.append('</div>')
    
    # Category panels
    html.append('<div class="avatar-options-container">')
    
    for i, category in enumerate(categories_data):
        active_class = 'active' if i == 0 else ''
        html.append(f'<div class="avatar-category {active_class}" data-category-panel="{i}">')
        html.append(f'<div class="avatar-category-title">{category["name"]}</div>')
        html.append('<div class="avatar-options">')
        
        # Render options in this category
        for value, option in category['options']:
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
        
        # End category panel
        html.append('</div></div>')
    
    html.append('</div>')
    
    # Add JavaScript for tabs functionality
    html.append('''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Tab switching functionality - use the specific ID we created
        const tabs = document.querySelectorAll('#avatar-selection-tabs .avatar-category-tab');
        const panels = document.querySelectorAll('.avatar-category');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const categoryIndex = this.getAttribute('data-category');
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show corresponding panel
                panels.forEach(panel => {
                    panel.classList.remove('active');
                    if (panel.getAttribute('data-category-panel') === categoryIndex) {
                        panel.classList.add('active');
                    }
                });
            });
        });
        
        // Avatar selection functionality
        const avatarOptions = document.querySelectorAll('.avatar-option');
        const avatarRadios = document.querySelectorAll('.avatar-radio');
        
        avatarOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Find the radio input within this option
                const radio = this.querySelector('input[type="radio"]');
                radio.checked = true;
                
                // Update selected styling
                avatarOptions.forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                
                // Update preview if available
                const currentAvatarImg = document.querySelector('.current-avatar img');
                if (currentAvatarImg) {
                    // Get the selected avatar image URL and add a timestamp to prevent caching
                    const selectedImgSrc = this.querySelector('img').src;
                    const timestamp = new Date().getTime();
                    
                    // Add or update timestamp parameter to force refresh
                    let newSrc = selectedImgSrc.split('?')[0]; // Remove any existing query params
                    newSrc = newSrc + '?_t=' + timestamp;
                    
                    // Update current avatar preview
                    currentAvatarImg.src = newSrc;
                }
                
                // Trigger change event for the radio button
                const event = new Event('change', { bubbles: true });
                radio.dispatchEvent(event);
            });
        });
    });
    </script>
    ''')
    
    # Close container
    html.append('</div>')
    
    return mark_safe('\n'.join(html))
