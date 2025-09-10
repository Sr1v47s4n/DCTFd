"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("events/", views.events, name="events"),
    path("events/create/", views.create_event, name="create_event"),
    path("events/<int:event_id>/", views.edit_event, name="edit_event"),
    # Challenge management URLs
    path("challenges/", views.challenges, name="challenges"),
    path("challenges/create/", views.create_challenge, name="create_challenge"),
    path("challenges/import/", views.challenges_import, name="challenges_import"),
    path("challenges/import/results/", views.challenges_import_results, name="challenges_import_results"),
    path("challenges/template/download/", views.download_challenge_template, name="download_challenge_template"),
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
        views.challenge_delete,
        name="challenge_delete",
    ),
    # Challenge Categories
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
    path(
        "challenges/<int:challenge_id>/toggle-visibility/",
        views.toggle_challenge_visibility,
        name="toggle_challenge_visibility",
    ),
    path(
        "challenges/<int:challenge_id>/export/",
        views.challenge_export,
        name="challenge_export",
    ),
    path(
        "challenges/<int:challenge_id>/duplicate/",
        views.challenge_duplicate,
        name="challenge_duplicate",
    ),
    path(
        "challenges/<int:challenge_id>/submissions/",
        views.challenge_submissions,
        name="challenge_submissions",
    ),
    path(
        "challenges/<int:challenge_id>/files/add/",
        views.challenge_file_add,
        name="challenge_file_add",
    ),
    path(
        "challenges/<int:challenge_id>/files/<int:file_id>/delete/",
        views.challenge_file_delete,
        name="challenge_file_delete",
    ),
    # Flag management URLs
    path("challenges/<int:challenge_id>/flags/add/", views.flag_add, name="flag_add"),
    path(
        "challenges/<int:challenge_id>/flags/<int:flag_id>/edit/",
        views.flag_edit,
        name="flag_edit",
    ),
    path(
        "challenges/<int:challenge_id>/flags/<int:flag_id>/delete/",
        views.flag_delete,
        name="flag_delete",
    ),
    # Hint management URLs
    path("challenges/<int:challenge_id>/hints/add/", views.hint_add, name="hint_add"),
    path(
        "challenges/<int:challenge_id>/hints/<int:hint_id>/edit/",
        views.hint_edit,
        name="hint_edit",
    ),
    path(
        "challenges/<int:challenge_id>/hints/<int:hint_id>/delete/",
        views.hint_delete,
        name="hint_delete",
    ),
    # Category management URLs
    path("categories/create/", views.category_create, name="category_create"),
    # Team management URLs
    path("teams/", views.teams, name="teams"),
    path("teams/<int:team_id>/", views.team_detail, name="team_detail"),
    # CTF control URLs
    path("ctf-controls/", views.ctf_controls, name="ctf_controls"),
    path("ctf/pause/", views.pause_ctf, name="pause_ctf"),
    path("ctf/resume/", views.resume_ctf, name="resume_ctf"),
    path("ctf/start/", views.start_ctf, name="start_ctf"),
    path("ctf/end/", views.end_ctf, name="end_ctf"),
    path("ctf/setup/", views.setup_ctf, name="setup_ctf"),
    path("ctf/reset/", views.reset_ctf, name="reset_ctf"),
    path("ctf/delete/", views.delete_ctf, name="delete_ctf"),
    path("ctf/announcement/", views.send_announcement, name="send_announcement"),
    # Scoreboard management URLs
    path("scoreboard/", views.scoreboard, name="scoreboard"),
    path("scoreboard/export/", views.export_scoreboard, name="export_scoreboard"),
    path(
        "scoreboard/export/<str:format>/",
        views.export_scoreboard,
        name="export_scoreboard_format",
    ),
    # Other URLs
    path("users/", views.users, name="users"),
    path("submissions/", views.submissions, name="submissions"),
]
