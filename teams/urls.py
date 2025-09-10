"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path("", views.teams_list, name="list"),
    path("create/", views.create_team, name="create"),
    path("join/", views.join_team, name="join"),
    path("profile/", views.team_profile, name="profile"),
    path("profile/edit/", views.edit_team_profile, name="edit_profile"),
    path("manage/", views.manage_team, name="manage"),
    path("members/", views.team_members, name="members"),
    path("members/invite/", views.invite_member, name="invite_member"),
    path("members/kick/<int:user_id>/", views.kick_member, name="kick_member"),
    path("members/promote/", views.promote_captain, name="promote_captain"),
    path("members/leave/", views.leave_team, name="leave_team"),
    path("settings/", views.team_settings, name="team_settings"),
    path("password/change/", views.change_team_password, name="change_password"),
    path("invites/cancel/<int:invite_id>/", views.cancel_invite, name="cancel_invite"),
    path("dissolve/", views.dissolve_team, name="dissolve"),
    path("<int:team_id>/", views.public_team_profile, name="public_profile"),
]
