"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, Q
from django.forms import modelformset_factory, inlineformset_factory
from django.core import serializers
from django.contrib.auth import get_user_model
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import io
import os
import datetime
import tempfile
import zipfile

from users.models import BaseUser
from teams.models import Team
from challenges.models import Challenge, Submission, ChallengeCategory, Flag, ChallengeFile
from event.models import Event
from .forms import (
    CustomFieldDefinitionForm,
    ChallengeForm,
    FlagForm,
    ChallengeFileForm,
    ChallengeCategoryForm,
)

def admin_required(view_func):
    """Decorator to ensure only admins can access views"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, _('You do not have permission to access this page.'))
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def dashboard(request):
    """Admin dashboard view with system statistics"""
    # Get counts for dashboard stats
    user_count = BaseUser.objects.count()
    organizer_count = BaseUser.objects.filter(type='organizer').count()
    admin_count = BaseUser.objects.filter(type='admin').count()
    team_count = Team.objects.count()
    challenge_count = Challenge.objects.count()
    submission_count = Submission.objects.count()
    event_count = Event.objects.count()
    
    # Recent user registrations
    recent_users = BaseUser.objects.order_by('-date_joined')[:10]
    
    context = {
        'user_count': user_count,
        'organizer_count': organizer_count,
        'admin_count': admin_count,
        'team_count': team_count,
        'challenge_count': challenge_count,
        'submission_count': submission_count,
        'event_count': event_count,
        'recent_users': recent_users,
    }
    
    return render(request, 'superadmin/dashboard.html', context)

@login_required
@admin_required
def users(request):
    """List all users"""
    users = BaseUser.objects.all().order_by('username')
    return render(request, 'superadmin/users/list.html', {'users': users})

@login_required
@admin_required
def create_user(request):
    """Create a new user"""
    # Placeholder for now, will implement form handling
    return render(request, 'superadmin/users/create.html')

@login_required
@admin_required
def edit_user(request, user_id):
    """Edit an existing user"""
    user = get_object_or_404(BaseUser, pk=user_id)
    return render(request, 'superadmin/users/edit.html', {'user': user})

@login_required
@admin_required
def organizers(request):
    """List all organizers"""
    organizers = BaseUser.objects.filter(type__in=['organizer', 'admin']).order_by('username')
    return render(request, 'superadmin/organizers/list.html', {'organizers': organizers})

@login_required
@admin_required
def settings(request):
    """System settings configuration"""
    # Get the active event
    from event.models import Event, EventSettings
    
    active_event = Event.objects.filter(status__in=["registration", "running"]).first()
    
    if request.method == 'POST':
        # Handle settings form submission
        if active_event:
            # Get or create event settings
            event_settings, created = EventSettings.objects.get_or_create(event=active_event)
            
            # Update custom fields settings
            event_settings.enable_user_custom_fields = bool(request.POST.get('enable_user_custom_fields'))
            event_settings.enable_team_custom_fields = bool(request.POST.get('enable_team_custom_fields'))
            event_settings.save()
            
            messages.success(request, _('Settings updated successfully.'))
    
    # Prepare context with current settings
    context = {}
    
    if active_event:
        try:
            event_settings = EventSettings.objects.get(event=active_event)
            context['enable_user_custom_fields'] = event_settings.enable_user_custom_fields
            context['enable_team_custom_fields'] = event_settings.enable_team_custom_fields
        except EventSettings.DoesNotExist:
            context['enable_user_custom_fields'] = False
            context['enable_team_custom_fields'] = False
    
    return render(request, 'superadmin/settings.html', context)

@login_required
@admin_required
def logs(request):
    """System logs viewer"""
    import os
    from django.conf import settings

    log_file_path = os.path.join(settings.BASE_DIR, "dctfd.log")
    logs_content = ""

    # Check if log file exists
    if os.path.exists(log_file_path):
        # Read the last 200 lines of the log file (most recent logs)
        try:
            with open(log_file_path, "r") as log_file:
                logs_content = log_file.readlines()
                # Get the last 200 lines
                logs_content = logs_content[-200:]
                logs_content = "".join(logs_content)
        except Exception as e:
            logs_content = f"Error reading log file: {str(e)}"
    else:
        logs_content = "No log file found. System activity logging will begin now."

    context = {"logs_content": logs_content}

    return render(request, "superadmin/logs.html", context)


@login_required
@admin_required
def clear_logs(request):
    """Clear the system logs file"""
    import os
    from django.conf import settings
    from django.http import JsonResponse
    import logging

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "Only POST requests are allowed"}
        )

    log_file_path = os.path.join(settings.BASE_DIR, "dctfd.log")

    try:
        # Clear the log file by opening it in write mode
        with open(log_file_path, "w") as log_file:
            log_file.write("")

        # Log that the logs were cleared
        logger = logging.getLogger("dctfd")
        logger.info(f"Logs cleared by admin user: {request.user.username}")

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
@admin_required
def statistics(request):
    """Detailed platform statistics"""
    # Import models
    from django.contrib.auth import get_user_model
    from teams.models import Team
    from event.models import Event
    from challenges.models import Challenge, Submission, ChallengeCategory
    from django.db.models import Count, Q
    from django.db.models.functions import TruncDay
    import json
    from datetime import timedelta
    from django.utils import timezone

    User = get_user_model()

    # Basic counts
    user_count = User.objects.count()
    team_count = Team.objects.count()
    challenge_count = Challenge.objects.count()
    submission_count = Submission.objects.count()
    category_count = ChallengeCategory.objects.count()

    # Get users registered per day (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    user_registrations = (
        User.objects.filter(date_joined__gte=thirty_days_ago)
        .annotate(date=TruncDay("date_joined"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    registration_dates = [
        reg["date"].strftime("%Y-%m-%d") for reg in user_registrations
    ]
    registration_counts = [reg["count"] for reg in user_registrations]

    # Get submissions per day (last 30 days)
    submissions_per_day = (
        Submission.objects.filter(submitted_at__gte=thirty_days_ago)
        .annotate(date=TruncDay("submitted_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    submission_dates = [sub["date"].strftime("%Y-%m-%d") for sub in submissions_per_day]
    submission_counts = [sub["count"] for sub in submissions_per_day]

    # Get solves by category
    category_solves = (
        Submission.objects.filter(is_correct=True)
        .values("challenge__category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    category_names = [
        cat["challenge__category__name"]
        for cat in category_solves
        if cat["challenge__category__name"]
    ]
    category_solve_counts = [
        cat["count"] for cat in category_solves if cat["challenge__category__name"]
    ]

    # Get challenges by category
    challenges_by_category = (
        Challenge.objects.values("category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    category_challenge_names = [
        cat["category__name"] for cat in challenges_by_category if cat["category__name"]
    ]
    category_challenge_counts = [
        cat["count"] for cat in challenges_by_category if cat["category__name"]
    ]

    # Get top teams
    top_teams = Team.objects.annotate(
        solve_count=Count("submissions", filter=Q(submissions__is_correct=True))
    ).order_by("-solve_count")[:5]

    # Success rate
    if submission_count > 0:
        success_rate = (
            Submission.objects.filter(is_correct=True).count() / submission_count
        ) * 100
    else:
        success_rate = 0

    # Recent submissions
    recent_submissions = Submission.objects.select_related(
        "user", "team", "challenge"
    ).order_by("-submitted_at")[:10]

    context = {
        "user_count": user_count,
        "team_count": team_count,
        "challenge_count": challenge_count,
        "submission_count": submission_count,
        "category_count": category_count,
        "success_rate": round(success_rate, 2),
        "registration_data": {
            "labels": json.dumps(registration_dates),
            "counts": json.dumps(registration_counts),
        },
        "submission_data": {
            "labels": json.dumps(submission_dates),
            "counts": json.dumps(submission_counts),
        },
        "category_solves": {
            "labels": json.dumps(category_names),
            "counts": json.dumps(category_solve_counts),
        },
        "category_challenges": {
            "labels": json.dumps(category_challenge_names),
            "counts": json.dumps(category_challenge_counts),
        },
        "top_teams": top_teams,
        "recent_submissions": recent_submissions,
    }

    return render(request, "superadmin/statistics.html", context)


@login_required
@admin_required
def submissions(request):
    """List and filter all flag submissions"""
    from challenges.models import Submission
    from django.db.models import Q
    from django.core.paginator import Paginator

    # Get filter parameters
    user_filter = request.GET.get("user", "")
    challenge_filter = request.GET.get("challenge", "")
    team_filter = request.GET.get("team", "")
    status_filter = request.GET.get("status", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    # Base queryset
    submissions = Submission.objects.select_related(
        "user", "team", "challenge"
    ).order_by("-submitted_at")

    # Apply filters
    if user_filter:
        submissions = submissions.filter(
            Q(user__username__icontains=user_filter)
            | Q(user__email__icontains=user_filter)
        )

    if challenge_filter:
        submissions = submissions.filter(
            Q(challenge__name__icontains=challenge_filter)
            | Q(challenge__category__name__icontains=challenge_filter)
        )

    if team_filter:
        submissions = submissions.filter(team__name__icontains=team_filter)

    if status_filter:
        if status_filter == "correct":
            submissions = submissions.filter(is_correct=True)
        elif status_filter == "incorrect":
            submissions = submissions.filter(is_correct=False)

    if date_from:
        try:
            from datetime import datetime

            date_from = datetime.strptime(date_from, "%Y-%m-%d")
            submissions = submissions.filter(submitted_at__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            from datetime import datetime, timedelta

            date_to = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(
                days=1
            )  # Include the full day
            submissions = submissions.filter(submitted_at__lte=date_to)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(submissions, 50)  # Show 50 submissions per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Get some stats for display
    total_count = submissions.count()
    correct_count = submissions.filter(is_correct=True).count()
    incorrect_count = submissions.filter(is_correct=False).count()

    if total_count > 0:
        success_rate = (correct_count / total_count) * 100
    else:
        success_rate = 0

    context = {
        "page_obj": page_obj,
        "total_count": total_count,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "success_rate": round(success_rate, 2),
        # Current filters for form repopulation
        "user_filter": user_filter,
        "challenge_filter": challenge_filter,
        "team_filter": team_filter,
        "status_filter": status_filter,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "superadmin/submissions.html", context)


@admin_required
def custom_fields(request):
    """List all custom fields"""
    from core.custom_fields import CustomFieldDefinition
    from django.contrib.contenttypes.models import ContentType
    from event.models import Event

    # Get active event
    active_event = Event.objects.filter(status__in=["registration", "running"]).first()

    if active_event:
        event_content_type = ContentType.objects.get_for_model(Event)
        user_fields = CustomFieldDefinition.objects.filter(
            content_type=event_content_type, object_id=active_event.id, field_for="user"
        ).order_by("order")

        team_fields = CustomFieldDefinition.objects.filter(
            content_type=event_content_type, object_id=active_event.id, field_for="team"
        ).order_by("order")
    else:
        user_fields = []
        team_fields = []

    context = {
        "user_fields": user_fields,
        "team_fields": team_fields,
    }

    return render(request, "superadmin/custom_fields/list.html", context)


@login_required
@admin_required
def create_custom_field(request):
    """Create a new custom field"""
    from superadmin.forms import CustomFieldDefinitionForm
    from event.models import Event
    from django.contrib.contenttypes.models import ContentType

    # Get field_for type from query parameters
    field_for = request.GET.get("type", "user")
    if field_for not in ["user", "team"]:
        field_for = "user"

    if request.method == "POST":
        form = CustomFieldDefinitionForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            
            # Get the current event or create a default one if none exists
            try:
                current_event = Event.objects.filter(status__in=['planning', 'registration', 'running', 'active']).first()
                if not current_event:
                    # If no active event, get the most recent one
                    current_event = Event.objects.order_by('-created_at').first()
                
                if current_event:
                    field.content_type = ContentType.objects.get_for_model(Event)
                    field.object_id = current_event.id
                else:
                    # If no event exists at all, we need to handle this case
                    # For now, we'll create a dummy reference or make fields nullable
                    messages.error(request, _("No event found. Please create an event first before adding custom fields."))
                    return render(request, "superadmin/custom_fields/form.html", {"form": form})
                    
            except Exception as e:
                messages.error(request, _("Error associating custom field with event: {}").format(str(e)))
                return render(request, "superadmin/custom_fields/form.html", {"form": form})
            
            field.save()
            messages.success(request, _("Custom field created successfully."))
            return redirect("superadmin:custom_fields")
    else:
        form = CustomFieldDefinitionForm(initial={"field_for": field_for})

    context = {
        "form": form,
    }

    return render(request, "superadmin/custom_fields/form.html", context)


@login_required
@admin_required
def edit_custom_field(request, field_id):
    """Edit an existing custom field"""
    from core.custom_fields import CustomFieldDefinition
    from superadmin.forms import CustomFieldDefinitionForm

    field = get_object_or_404(CustomFieldDefinition, id=field_id)

    if request.method == "POST":
        form = CustomFieldDefinitionForm(request.POST, instance=field)
        if form.is_valid():
            form.save()
            messages.success(request, _("Custom field updated successfully."))
            return redirect("superadmin:custom_fields")
    else:
        form = CustomFieldDefinitionForm(instance=field)

    context = {
        "form": form,
        "field": field,
    }

    return render(request, "superadmin/custom_fields/form.html", context)


@login_required
@admin_required
def delete_custom_field(request, field_id):
    """Delete a custom field"""
    from core.custom_fields import CustomFieldDefinition

    field = get_object_or_404(CustomFieldDefinition, id=field_id)

    if request.method == "POST":
        field.delete()
        messages.success(request, _("Custom field deleted successfully."))
        return redirect("superadmin:custom_fields")

    context = {
        "field": field,
    }

    return render(request, "superadmin/custom_fields/delete.html", context)


# Challenge Management Views
@login_required
@admin_required
def challenges(request):
    """List all challenges"""
    challenges = Challenge.objects.all().order_by('-created_at')
    # Only show non-hidden categories by default
    categories = ChallengeCategory.objects.filter(is_hidden=False).order_by(
        "order", "name"
    )

    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        try:
            selected_category = ChallengeCategory.objects.get(id=category_id)
            challenges = challenges.filter(category=selected_category)
            context = {
                'challenges': challenges,
                'categories': categories,
                'selected_category': selected_category
            }
        except ChallengeCategory.DoesNotExist:
            context = {
                'challenges': challenges,
                'categories': categories
            }
    else:
        context = {
            'challenges': challenges,
            'categories': categories
        }

    # Add form for adding new categories via modal
    context["form"] = ChallengeCategoryForm()

    # Filter by active status if provided
    show_active_only = request.GET.get('active') == 'true'
    if show_active_only:
        challenges = challenges.filter(is_visible=True)
        context['show_active_only'] = True

    context['challenges'] = challenges

    return render(request, 'superadmin/challenges/list.html', context)


@login_required
@admin_required
def challenge_detail(request, challenge_id):
    """View challenge details"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    submissions = Submission.objects.filter(challenge=challenge).order_by('-submitted_at')
    
    context = {
        'challenge': challenge,
        'submissions': submissions
    }
    
    return render(request, 'superadmin/challenges/detail.html', context)


@login_required
@admin_required
def create_challenge(request):
    """Create a new challenge"""
    categories = ChallengeCategory.objects.all()

    # Create formsets for flags and files
    FlagFormSet = inlineformset_factory(
        Challenge, Flag, form=FlagForm, extra=1, can_delete=True
    )
    FileFormSet = inlineformset_factory(
        Challenge, ChallengeFile, form=ChallengeFileForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        # Create a new challenge form instance with POST data
        form = ChallengeForm(request.POST)

        if form.is_valid():
            # Create a new challenge instance but don't save yet
            challenge = form.save(commit=False)
            challenge.created_by = request.user

            # Get the active event (assuming there's always an active event)
            active_event = Event.objects.filter(
                status__in=["registration", "running"]
            ).first()
            if not active_event:
                messages.error(
                    request, _("No active event found. Please create an event first.")
                )
                flag_formset = FlagFormSet(request.POST)
                file_formset = FileFormSet(request.POST, request.FILES)
                return render(
                    request,
                    "superadmin/challenges/form.html",
                    {
                        "categories": categories,
                        "title": "Create Challenge",
                        "form": form,
                        "formset": flag_formset,
                        "files_formset": file_formset,
                    },
                )

            challenge.event = active_event
            challenge.save()

            # Process flag formset
            flag_formset = FlagFormSet(request.POST, instance=challenge)
            if flag_formset.is_valid():
                flag_formset.save()

            # Process file formset
            file_formset = FileFormSet(request.POST, request.FILES, instance=challenge)
            if file_formset.is_valid():
                file_formset.save()

            messages.success(request, _('Challenge created successfully.'))
            return redirect('superadmin:challenge_detail', challenge_id=challenge.id)
        else:
            # Form is invalid, show errors
            flag_formset = FlagFormSet(request.POST)
            file_formset = FileFormSet(request.POST, request.FILES)
    else:
        # Display empty form
        form = ChallengeForm(initial={"is_visible": True, "state": "visible"})
        flag_formset = FlagFormSet()
        file_formset = FileFormSet()

    context = {
        "categories": categories,
        "title": "Create Challenge",
        "form": form,
        "formset": flag_formset,
        "files_formset": file_formset,
    }
    return render(request, "superadmin/challenges/form.html", context)


@login_required
@admin_required
def edit_challenge(request, challenge_id):
    """Edit an existing challenge"""
    from django.forms import inlineformset_factory

    challenge = get_object_or_404(Challenge, id=challenge_id)
    categories = ChallengeCategory.objects.all()

    # Create formsets for flags and files
    FlagFormSet = inlineformset_factory(
        Challenge, Flag, form=FlagForm, extra=1, can_delete=True
    )
    FileFormSet = inlineformset_factory(
        Challenge, ChallengeFile, form=ChallengeFileForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = ChallengeForm(request.POST, instance=challenge)
        flag_formset = FlagFormSet(request.POST, instance=challenge)
        file_formset = FileFormSet(request.POST, request.FILES, instance=challenge)

        if form.is_valid() and flag_formset.is_valid() and file_formset.is_valid():
            # Save challenge form
            form.save()

            # Save formsets
            flag_formset.save()
            file_formset.save()

            messages.success(request, _('Challenge updated successfully.'))
            return redirect("superadmin:challenge_detail", challenge_id=challenge.id)
        else:
            for error in form.errors:
                messages.error(request, f"{error}: {form.errors[error]}")
    else:
        # Create form with challenge data
        form = ChallengeForm(instance=challenge)
        flag_formset = FlagFormSet(instance=challenge)
        file_formset = FileFormSet(instance=challenge)

    context = {
        "challenge": challenge,
        "categories": categories,
        "title": "Edit Challenge",
        "form": form,
        "formset": flag_formset,
        "files_formset": file_formset,
    }
    return render(request, "superadmin/challenges/form.html", context)


@login_required
@admin_required
def delete_challenge(request, challenge_id):
    """Delete a challenge"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    
    if request.method == 'POST':
        challenge.delete()
        messages.success(request, _('Challenge deleted successfully.'))
        return redirect('superadmin:challenges')
    
    return render(request, 'superadmin/challenges/delete.html', {
        'challenge': challenge
    })


@login_required
@admin_required
def categories(request):
    """List all challenge categories"""
    # Show all categories including hidden ones for admins
    categories = ChallengeCategory.objects.all().order_by("order", "name")
    form = ChallengeCategoryForm()  # Add form for new category creation

    return render(
        request,
        "superadmin/challenges/categories.html",
        {"categories": categories, "form": form},
    )


@login_required
@admin_required
def add_category(request):
    """Add a new challenge category"""
    if request.method == 'POST':
        form = ChallengeCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, _("Category added successfully."))

            # If it's an AJAX request, return JSON response
            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest" or "application/json" in request.headers.get(
                "Accept", ""
            ):
                return JsonResponse(
                    {
                        "success": True,
                        "category_id": category.id,
                        "category_name": category.name,
                    }
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            # If it's an AJAX request, return error
            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest" or "application/json" in request.headers.get(
                "Accept", ""
            ):
                return JsonResponse({"success": False, "message": "Validation error"})

        return redirect('superadmin:categories')

    # If GET, redirect to the categories page with the form
    return redirect('superadmin:categories')


@login_required
@admin_required
def edit_category(request, category_id):
    """Edit an existing challenge category"""
    category = get_object_or_404(ChallengeCategory, id=category_id)

    if request.method == 'POST':
        form = ChallengeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category updated successfully.'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return redirect('superadmin:categories')

    # If GET, show the edit form
    form = ChallengeCategoryForm(instance=category)
    return render(
        request,
        "superadmin/challenges/edit_category.html",
        {"form": form, "category": category},
    )


@login_required
@admin_required
def delete_category(request, category_id):
    """Delete a challenge category"""
    category = get_object_or_404(ChallengeCategory, id=category_id)

    if request.method == 'POST':
        try:
            # Check if category has challenges
            challenge_count = Challenge.objects.filter(category=category).count()

            if challenge_count > 0:
                hide_category = request.POST.get("hide_instead", False) == "true"

                if hide_category:
                    # Set the is_hidden flag to true
                    category.is_hidden = True
                    category.save()
                    messages.success(request, _("Category hidden successfully."))
                else:
                    messages.warning(
                        request,
                        _(
                            "This category has associated challenges. Reassign them before deleting or choose to hide instead."
                        ),
                    )
                    return render(
                        request,
                        "superadmin/challenges/delete_category.html",
                        {"category": category, "challenge_count": challenge_count},
                    )
            else:
                category.delete()
                messages.success(request, _("Category deleted successfully."))
        except Exception as e:
            messages.error(request, str(e))

        return redirect('superadmin:categories')

    # Show confirmation page with option to hide instead of delete
    challenge_count = Challenge.objects.filter(category=category).count()
    return render(
        request,
        "superadmin/challenges/delete_category.html",
        {"category": category, "challenge_count": challenge_count},
    )


@login_required
@admin_required
def toggle_category_visibility(request, category_id):
    """Toggle the visibility of a challenge category"""
    if request.method == "POST":
        category = get_object_or_404(ChallengeCategory, id=category_id)
        category.is_hidden = not category.is_hidden
        category.save()

        status = "hidden" if category.is_hidden else "visible"
        messages.success(request, _(f'Category "{category.name}" is now {status}.'))

    return redirect('superadmin:categories')

@login_required
@admin_required
def import_export(request):
    """Display import/export options"""
    # Define exportable models for CSV
    exportable_models = [
        {"name": "Users", "value": "users", "description": "User accounts"},
        {"name": "Teams", "value": "teams", "description": "Teams and their members"},
        {"name": "Challenges", "value": "challenges", "description": "Challenges with flags and hints"},
        {"name": "Categories", "value": "categories", "description": "Challenge categories"},
        {"name": "Submissions", "value": "submissions", "description": "Flag submissions"},
        {"name": "Scoreboard", "value": "scoreboard", "description": "Team and user scores"},
    ]
    
    return render(request, 'superadmin/import_export.html', {
        'exportable_models': exportable_models
    })

@login_required
@admin_required
def export_json(request):
    """Export all data to JSON files in a ZIP archive"""
    # Create temporary directory to store JSON files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Get all models from our apps
        apps_to_export = ['users', 'teams', 'challenges', 'event', 'core']
        
        files_created = []
        
        # For each app, export all models
        for app_name in apps_to_export:
            app_models = apps.get_app_config(app_name).get_models()
            
            for model in app_models:
                model_name = model.__name__
                file_name = f"{app_name}_{model_name}.json"
                file_path = os.path.join(temp_dir, file_name)
                
                try:
                    # Get all objects for this model
                    queryset = model.objects.all()
                    
                    # Skip empty querysets
                    if not queryset.exists():
                        continue
                    
                    # Serialize to JSON
                    with open(file_path, 'w') as json_file:
                        # Custom serialization to make it more human-readable
                        serialized_data = serializers.serialize('json', queryset, indent=4)
                        json_file.write(serialized_data)
                    
                    files_created.append(file_name)
                except Exception as e:
                    # Log the error but continue with other models
                    print(f"Error exporting {model_name}: {str(e)}")
                    continue
        
        # Create a ZIP file with all JSON files
        zip_file_path = os.path.join(temp_dir, 'dctfd_export.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file_name in files_created:
                file_path = os.path.join(temp_dir, file_name)
                zipf.write(file_path, arcname=file_name)
        
        # Read the ZIP file and serve it as a response
        with open(zip_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename=dctfd_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
            
            return response

@login_required
@admin_required
@csrf_exempt
def import_json(request):
    """Import data from JSON files"""
    if request.method == 'POST' and request.FILES.get('json_file'):
        try:
            uploaded_file = request.FILES['json_file']
            
            # Check if it's a ZIP file
            if uploaded_file.name.endswith('.zip'):
                # Create a temporary directory to extract files
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save the ZIP file
                    zip_path = os.path.join(temp_dir, 'upload.zip')
                    with open(zip_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                    
                    # Extract the ZIP file
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        zipf.extractall(temp_dir)
                    
                    # Process each JSON file
                    success_count = 0
                    error_count = 0
                    for file_name in os.listdir(temp_dir):
                        if file_name.endswith('.json'):
                            try:
                                with open(os.path.join(temp_dir, file_name), 'r') as f:
                                    process_json_import(f.read())
                                success_count += 1
                            except Exception as e:
                                error_count += 1
                                messages.warning(request, _(f'Error importing {file_name}: {str(e)}'))
                    
                    if success_count > 0:
                        messages.success(request, _(f'Successfully imported {success_count} files from ZIP archive.'))
                    if error_count > 0:
                        messages.warning(request, _(f'Failed to import {error_count} files from ZIP archive.'))
            else:
                # Single JSON file
                content = uploaded_file.read().decode('utf-8')
                try:
                    process_json_import(content)
                    messages.success(request, _('Successfully imported data from JSON file.'))
                except Exception as e:
                    messages.error(request, _(f'Error importing JSON data: {str(e)}'))
                
        except Exception as e:
            messages.error(request, _(f'Error importing data: {str(e)}'))
        
        return redirect('superadmin:import_export')
    
    return redirect('superadmin:import_export')

def process_json_import(json_content):
    """Process a single JSON file for import"""
    try:
        data = json.loads(json_content)
        
        # Empty data check
        if not data:
            return
        
        # Extract model name from the first object
        model_name = data[0]['model']
        app_label, model_name = model_name.split('.')
        
        # Get the model class
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise Exception(f"Model {model_name} not found in app {app_label}")
        
        # Delete existing objects if the model is not User
        if model.__name__ not in ['BaseUser']:
            model.objects.all().delete()
        
        # Use Django's built-in deserializer with error handling
        for obj in serializers.deserialize('json', json_content):
            try:
                obj.save()
            except Exception as e:
                print(f"Error saving object: {str(e)}")
                continue
    except Exception as e:
        print(f"Error processing JSON import: {str(e)}")
        raise

@login_required
@admin_required
def export_csv(request, model_type):
    """Export data to CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_type}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        User = get_user_model()
        
        # Create CSV writer
        writer = csv.writer(response)
        
        if model_type == 'users':
            # Export users
            writer.writerow(['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'type'])
            users = User.objects.all()
            for user in users:
                writer.writerow([
                    user.id, 
                    user.username, 
                    user.email, 
                    user.first_name, 
                    user.last_name, 
                    user.is_active, 
                    user.date_joined, 
                    user.last_login,
                    user.type
                ])
        
        elif model_type == 'teams':
            # Export teams
            writer.writerow(['id', 'name', 'description', 'created_at', 'members'])
            teams = Team.objects.all()
            for team in teams:
                members = ', '.join([u.username for u in team.members.all()])
                writer.writerow([
                    team.id, 
                    team.name, 
                    team.description, 
                    team.created_at,
                    members
                ])
        
        elif model_type == 'challenges':
            # Export challenges
            writer.writerow(['id', 'name', 'description', 'category', 'value', 'type', 'difficulty', 'flags', 'is_visible'])
            challenges = Challenge.objects.all()
            for challenge in challenges:
                flags = ', '.join([f.flag for f in challenge.flag_set.all()])
                writer.writerow([
                    challenge.id, 
                    challenge.name, 
                    challenge.description, 
                    challenge.category.name if challenge.category else 'None',
                    challenge.value,
                    challenge.type,
                    challenge.difficulty,
                    flags,
                    challenge.is_visible
                ])
        
        elif model_type == 'categories':
            # Export categories
            writer.writerow(['id', 'name', 'description', 'color', 'icon', 'is_hidden'])
            categories = ChallengeCategory.objects.all()
            for category in categories:
                writer.writerow([
                    category.id, 
                    category.name, 
                    category.description, 
                    category.color,
                    category.icon,
                    category.is_hidden
                ])
        
        elif model_type == 'submissions':
            # Export submissions
            writer.writerow(['id', 'user', 'team', 'challenge', 'flag_submitted', 'is_correct', 'submitted_at', 'ip_address'])
            submissions = Submission.objects.all()
            for submission in submissions:
                writer.writerow([
                    submission.id, 
                    submission.user.username, 
                    submission.team.name if submission.team else 'None', 
                    submission.challenge.name,
                    submission.flag_submitted,
                    submission.is_correct,
                    submission.submitted_at,
                    submission.ip_address
                ])
        
        elif model_type == 'scoreboard':
            # Export scoreboard data
            writer.writerow(['id', 'name', 'type', 'score', 'last_score_update', 'solves'])
            
            # Team scores
            teams = Team.objects.all().annotate(solve_count=Count('submissions', filter=Q(submissions__is_correct=True)))
            for team in teams:
                writer.writerow([
                    team.id,
                    team.name,
                    'team',
                    team.score,
                    team.last_score_update,
                    team.solve_count
                ])
            
            # User scores (users without teams)
            users = User.objects.filter(team__isnull=True).annotate(solve_count=Count('submissions', filter=Q(submissions__is_correct=True)))
            for user in users:
                writer.writerow([
                    user.id,
                    user.username,
                    'user',
                    user.score,
                    user.last_score_update,
                    user.solve_count
                ])
        
        return response
    except Exception as e:
        messages.error(request, _(f'Error exporting CSV: {str(e)}'))
        return redirect('superadmin:import_export')

@login_required
@admin_required
@csrf_exempt
def import_csv(request, model_type):
    """Import data from CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            User = get_user_model()
            
            if model_type == 'users':
                # Import users - don't delete existing users
                for row in reader:
                    try:
                        user, created = User.objects.get_or_create(
                            username=row['username'],
                            defaults={
                                'email': row['email'],
                                'first_name': row['first_name'],
                                'last_name': row['last_name'],
                                'is_active': row['is_active'] == 'True',
                                'type': row.get('type', 'user')
                            }
                        )
                        
                        if not created:
                            # Update existing user
                            user.email = row['email']
                            user.first_name = row['first_name']
                            user.last_name = row['last_name']
                            user.is_active = row['is_active'] == 'True'
                            user.type = row.get('type', 'user')
                            user.save()
                    except Exception as e:
                        messages.warning(request, _(f'Error importing user {row.get("username")}: {str(e)}'))
            
            elif model_type == 'teams':
                # Import teams
                if request.POST.get('clear_existing') == 'yes':
                    Team.objects.all().delete()
                
                for row in reader:
                    try:
                        team, created = Team.objects.get_or_create(
                            name=row['name'],
                            defaults={
                                'description': row['description'],
                            }
                        )
                        
                        # Process members
                        if 'members' in row and row['members']:
                            member_usernames = [username.strip() for username in row['members'].split(',')]
                            for username in member_usernames:
                                try:
                                    user = User.objects.get(username=username)
                                    team.members.add(user)
                                except User.DoesNotExist:
                                    messages.warning(request, _(f'User {username} not found for team {team.name}'))
                    except Exception as e:
                        messages.warning(request, _(f'Error importing team {row.get("name")}: {str(e)}'))
            
            elif model_type == 'challenges':
                # Import challenges
                if request.POST.get('clear_existing') == 'yes':
                    Challenge.objects.all().delete()
                
                for row in reader:
                    try:
                        # Get or create category
                        category = None
                        if row['category'] and row['category'] != 'None':
                            category, _ = ChallengeCategory.objects.get_or_create(name=row['category'])
                        
                        # Create challenge
                        challenge, created = Challenge.objects.get_or_create(
                            name=row['name'],
                            defaults={
                                'description': row['description'],
                                'category': category,
                                'value': int(row['value']),
                                'type': row['type'],
                                'difficulty': int(row['difficulty']),
                                'is_visible': row['is_visible'] == 'True'
                            }
                        )
                        
                        # Process flags
                        if 'flags' in row and row['flags']:
                            # Clear existing flags if this is an update
                            if not created:
                                Flag.objects.filter(challenge=challenge).delete()
                            
                            flag_values = [flag.strip() for flag in row['flags'].split(',')]
                            for flag_value in flag_values:
                                Flag.objects.create(
                                    challenge=challenge,
                                    flag=flag_value,
                                    type='static'
                                )
                    except Exception as e:
                        messages.warning(request, _(f'Error importing challenge {row.get("name")}: {str(e)}'))
            
            elif model_type == 'categories':
                # Import categories
                if request.POST.get('clear_existing') == 'yes':
                    ChallengeCategory.objects.all().delete()
                
                for row in reader:
                    try:
                        ChallengeCategory.objects.get_or_create(
                            name=row['name'],
                            defaults={
                                'description': row['description'],
                                'color': row['color'],
                                'icon': row['icon'],
                                'is_hidden': row['is_hidden'] == 'True'
                            }
                        )
                    except Exception as e:
                        messages.warning(request, _(f'Error importing category {row.get("name")}: {str(e)}'))
            
            elif model_type == 'submissions':
                # Import submissions
                if request.POST.get('clear_existing') == 'yes':
                    Submission.objects.all().delete()
                
                for row in reader:
                    try:
                        # Get required objects
                        user = User.objects.get(username=row['user'])
                        challenge = Challenge.objects.get(name=row['challenge'])
                        team = None
                        if row['team'] and row['team'] != 'None':
                            team = Team.objects.get(name=row['team'])
                        
                        # Create submission
                        Submission.objects.create(
                            user=user,
                            team=team,
                            challenge=challenge,
                            flag_submitted=row['flag_submitted'],
                            is_correct=row['is_correct'] == 'True',
                            submitted_at=datetime.datetime.fromisoformat(row['submitted_at']),
                            ip_address=row['ip_address']
                        )
                    except Exception as e:
                        messages.warning(request, _(f'Error importing submission: {str(e)}'))
            
            messages.success(request, _(f'Successfully imported {model_type} from CSV.'))
        except Exception as e:
            messages.error(request, _(f'Error importing CSV: {str(e)}'))
    
    return redirect('superadmin:import_export')
