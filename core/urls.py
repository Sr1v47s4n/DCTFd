"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path("", views.home, name="home"),
    path("index", views.home, name="index"),
    path("challenges", views.challenges, name="challenges"),
    path("scoreboard", views.scoreboard, name="scoreboard"),
    path("notifications", views.notifications, name="notifications"),
    path("rules", views.rules, name="rules"),
    path("faq", views.faq, name="faq"),
    path("privacy", views.privacy, name="privacy"),
    path("about", views.about, name="about"),
    # Notification management
    path(
        "notification-manager", views.notification_manager, name="notification_manager"
    ),
    path("send-notification", views.send_notification, name="send_notification"),
]
