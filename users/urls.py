"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        views.ActivateAccountView.as_view(),
        name="activate",
    ),
    path("confirm/<data>/", views.confirm_email, name="confirm_email"),
    path("confirm/", views.resend_confirmation, name="resend_confirmation"),
    path("verify/", views.verify_account, name="verify_account"),
    # OAuth routes
    path("oauth/", views.oauth_login, name="oauth_login"),
    path("oauth/callback", views.oauth_callback, name="oauth_callback"),
    # Password Management
    path(
        "password/change/", views.PasswordChangeView.as_view(), name="password_change"
    ),
    path(
        "password/reset/",
        views.CustomPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "first-login/", views.FirstLoginPasswordChangeView.as_view(), name="first_login"
    ),
    # Profile Management
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path(
        "profile/<str:username>/",
        views.PublicProfileView.as_view(),
        name="public_profile",
    ),
    path("settings/", views.settings, name="settings"),
    # Two-factor auth
    path("2fa/", views.two_factor_setup, name="two_factor_setup"),
    path("2fa/verify", views.two_factor_verify, name="two_factor_verify"),
    path("2fa/toggle", views.two_factor_toggle, name="two_factor_toggle"),
    path("2fa/disable", views.two_factor_disable, name="two_factor_disable"),
    # APIs
    path("api/user/", views.UserAPI.as_view(), name="api_user"),
    path(
        "api/team-search/", views.TeamMemberSearchAPI.as_view(), name="api_team_search"
    ),
]
