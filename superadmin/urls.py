"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.users, name="users"),
    path("users/create/", views.create_user, name="create_user"),
    path("users/<int:user_id>/", views.edit_user, name="edit_user"),
    path("organizers/", views.organizers, name="organizers"),
    path("settings/", views.settings, name="settings"),
    path("logs/", views.logs, name="logs"),
    path("logs/clear/", views.clear_logs, name="clear_logs"),
    path("statistics/", views.statistics, name="statistics"),
    path("submissions/", views.submissions, name="submissions"),
    # Import/Export
    path("import-export/", views.import_export, name="import_export"),
    path("export/json/", views.export_json, name="export_json"),
    path("import/json/", views.import_json, name="import_json"),
    path("export/csv/<str:model_type>/", views.export_csv, name="export_csv"),
    path("import/csv/<str:model_type>/", views.import_csv, name="import_csv"),
    # Challenge Management
    path("challenges/", views.challenges, name="challenges"),
    path("challenges/create/", views.create_challenge, name="add_challenge"),
    path(
        "challenges/<int:challenge_id>/",
        views.challenge_detail,
        name="challenge_detail",
    ),
    path(
        "challenges/<int:challenge_id>/edit/",
        views.edit_challenge,
        name="edit_challenge",
    ),
    path(
        "challenges/<int:challenge_id>/delete/",
        views.delete_challenge,
        name="delete_challenge",
    ),
    # Categories Management
    path("challenges/categories/", views.categories, name="categories"),
    path("challenges/categories/add/", views.add_category, name="add_category"),
    path(
        "challenges/categories/<int:category_id>/edit/",
        views.edit_category,
        name="edit_category",
    ),
    path(
        "challenges/categories/<int:category_id>/delete/",
        views.delete_category,
        name="delete_category",
    ),
    path(
        "challenges/categories/<int:category_id>/toggle/",
        views.toggle_category_visibility,
        name="toggle_category_visibility",
    ),
    # Custom Fields Management
    path("custom-fields/", views.custom_fields, name="custom_fields"),
    path(
        "custom-fields/create/", views.create_custom_field, name="create_custom_field"
    ),
    path(
        "custom-fields/<int:field_id>/",
        views.edit_custom_field,
        name="edit_custom_field",
    ),
    path(
        "custom-fields/<int:field_id>/delete/",
        views.delete_custom_field,
        name="delete_custom_field",
    ),
]
