"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.utils.deprecation import MiddlewareMixin

class NoCacheAvatarMiddleware(MiddlewareMixin):
    """
    Middleware that adds cache control headers to avatar URLs
    to prevent browsers from caching avatars
    """
    
    def process_response(self, request, response):
        # Only add no-cache headers for avatar URLs
        if 'avatars/' in request.path:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
