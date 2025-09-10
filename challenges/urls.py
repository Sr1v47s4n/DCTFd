"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('', views.challenge_list, name='list'),
    path('<int:challenge_id>/', views.challenge_detail, name='detail'),
    path('<int:challenge_id>/submit/', views.submit_flag, name='submit_flag'),
    path('hint/<int:hint_id>/unlock/', views.unlock_hint, name='unlock_hint'),
    path('file/<int:file_id>/download/', views.download_file, name='download_file'),
]
