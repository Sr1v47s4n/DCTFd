"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from . import views

app_name = 'event'

urlpatterns = [
    path('setup/', views.event_setup, name='setup'),
    path('save/', views.event_save, name='save'),
]
