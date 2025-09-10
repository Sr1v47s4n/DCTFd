"""
DCTFd URL Configuration

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", include("core.urls")),
    path("event/", include("event.urls")),
    # path("admin/", admin.site.urls),  # Django admin site - removed due to admin app not being properly configured
    path("organizer/", include("organizer.urls")),  # Organizer panel
    path("superadmin/", include("superadmin.urls")),  # Super admin panel
    path(
        "account/", include("users.urls")
    ),  # Add user authentication and profile routes
    path("challenges/", include("challenges.urls")),  # Add challenges routes
    path("teams/", include("teams.urls")),  # Add teams routes
    # Authentication URLs
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]

# Always serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
