"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify

from event.models import Event
from challenges.models import Challenge, ChallengeCategory, Submission
from teams.models import Team
from users.models import BaseUser
from core.models import Notification
from core.notification_service import NotificationService

def home(request):
    """
    Home page view.
    If no events exist yet, redirect to the setup page.
    Otherwise, show the home page with the active event.
    In development mode, redirect to login page.
    """
    # Check for development mode
    if settings.DEV_MODE and request.user.is_anonymous:
        messages.info(request, _('Development mode is active. Please log in with username: admin, password: admin'))
        return redirect('users:login')

    # Check if any events exist
    if not Event.objects.exists():
        # Create default event using settings
        # from django.utils.text import slugify
        # current_event = Event.objects.create(
        #     name=settings.EVENT_NAME,
        #     slug=slugify(settings.EVENT_NAME),
        #     description=f"{settings.EVENT_NAME} CTF Event",
        #     short_description=f"{settings.EVENT_NAME} CTF Event",
        #     start_time=timezone.now(),
        #     end_time=timezone.now() + timezone.timedelta(days=30),
        #     registration_start=timezone.now(),
        #     registration_end=timezone.now() + timezone.timedelta(days=30),
        #     status='running',
        #     is_visible=True
        # )
        # messages.success(request, _(f"Event {settings.EVENT_NAME} has been created."))\
        # Redirect to event setup page if no events exist
        messages.info(
            request, _("No events exist yet. Please complete the event setup.")
        )
        return redirect("event:setup")
    else:
        # Get the active event (single event system)
        current_event = Event.objects.first()

        # Update event name from settings if changed
        if current_event.name != settings.EVENT_NAME:
            current_event.name = settings.EVENT_NAME
            current_event.slug = slugify(settings.EVENT_NAME)
            current_event.save()

    # Get statistics for the homepage
    total_users = BaseUser.objects.filter(type='user').count()
    total_teams = Team.objects.count()
    total_challenges = Challenge.objects.filter(event=current_event).count()
    total_solves = Submission.objects.filter(
        challenge__event=current_event, is_correct=True
    ).count()

    # Get user-specific data if authenticated
    user_team = None
    user_solved = 0
    team_solved = 0

    if request.user.is_authenticated and request.user.type == "user":
        # Get user's personal solved challenges
        user_solved = (
            Submission.objects.filter(
                user=request.user, is_correct=True, challenge__event=current_event
            )
            .values_list("challenge_id", flat=True)
            .distinct()
            .count()
        )

        # Get user's team if they have one
        if hasattr(request.user, "team") and request.user.team:
            user_team = request.user.team
            team_solved = (
                Submission.objects.filter(
                    team=user_team, is_correct=True, challenge__event=current_event
                )
                .values_list("challenge_id", flat=True)
                .distinct()
                .count()
            )

    context = {
        "event": current_event,
        "total_users": total_users,
        "total_teams": total_teams,
        "total_challenges": total_challenges,
        "total_solves": total_solves,
        "user_team": user_team,
        "user_solved": user_solved,
        "team_solved": team_solved,
        "is_captain": request.user.is_authenticated
        and hasattr(request.user, "team")
        and request.user.team
        and request.user == request.user.team.captain,
    }

    return render(request, 'core/home.html', context)

@login_required
def challenges(request):
    """
    Redirect to the challenges app.
    This is kept for backwards compatibility.
    """
    return redirect("challenges:list")

def scoreboard(request):
    """
    Scoreboard page showing team/user rankings with enhanced data for visualization.
    """
    # Get current event (single event system)
    current_event = Event.objects.filter(is_visible=True).first()

    if not current_event:
        messages.error(request, _('No active CTF event is currently available.'))
        return redirect('core:home')

    # Get challenge statistics
    total_challenges = Challenge.objects.filter(
        event=current_event, is_visible=True
    ).count()
    total_solves = Submission.objects.filter(
        challenge__event=current_event, is_correct=True
    ).count()

    # Get challenge categories for filtering
    categories = ChallengeCategory.objects.filter(
        challenges__event=current_event
    ).distinct()

    # Always use team mode
    # Get teams with scores
    teams = Team.objects.all().order_by("-score", "last_active")

    # Calculate solved challenges percentage for each team
    for team in teams:
        solved_challenges = (
            Submission.objects.filter(
                team=team, is_correct=True, challenge__event=current_event
            )
            .values_list("challenge", flat=True)
            .distinct()
            .count()
        )

        team.solved_count = solved_challenges
        team.solved_percent = int(
            (solved_challenges / total_challenges * 100) if total_challenges > 0 else 0
        )

        # Calculate score change in the last 24 hours
        recent_submissions = Submission.objects.filter(
            team=team,
            is_correct=True,
            challenge__event=current_event,
            submitted_at__gte=timezone.now() - timezone.timedelta(hours=24),
        )
        team.score_change = sum(sub.challenge.value for sub in recent_submissions)

    scoreboard_entries = teams

    # Generate data for score graph
    score_graph_data = generate_team_score_graph_data(teams, current_event)

    # Get current user's team ID for highlighting
    current_user_id = None
    if (
        request.user.is_authenticated
        and hasattr(request.user, "team")
        and request.user.team
    ):
        current_user_id = request.user.team.id

    context = {
        "event": current_event,
        "categories": categories,
        "scoreboard_entries": scoreboard_entries,
        "total_challenges": total_challenges,
        "total_solves": total_solves,
        "score_graph_data": score_graph_data,
        "current_user_id": current_user_id,
        "is_team_scoreboard": True,  # Always team mode for now
        "is_team_member": request.user.is_authenticated
        and hasattr(request.user, "team")
        and request.user.team,
        "is_captain": request.user.is_authenticated
        and hasattr(request.user, "team")
        and request.user.team
        and request.user == request.user.team.captain,
    }

    return render(request, 'core/scoreboard.html', context)


def generate_team_score_graph_data(teams, event):
    """
    Generate JSON data for team score progression graph.
    """
    import json
    from django.db.models import Sum, Count
    from challenges.models import Submission
    import datetime

    # Dictionary to store score progression data
    score_data = {}

    # Get all correct submissions ordered by timestamp
    submissions = Submission.objects.filter(
        team__isnull=False, is_correct=True, challenge__event=event
    ).order_by("submitted_at")

    # Track each team's score over time
    team_scores = {team.id: 0 for team in teams}

    # Get the event start time for timestamp calculation
    event_start = (
        event.start_time
        if event and event.start_time
        else (
            submissions.first().submitted_at
            if submissions.exists()
            else datetime.datetime.now()
        )
    )

    # Generate timestamps and scores
    for submission in submissions:
        # Skip if not a team submission
        if not submission.team:
            continue

        # Update team's score
        team_id = submission.team.id
        team_scores[team_id] += submission.challenge.value

        # Calculate timestamp in seconds since event start
        timestamp = int((submission.submitted_at - event_start).total_seconds())

        # Ensure timestamp exists in the data
        if timestamp not in score_data:
            score_data[timestamp] = {}

            # Add current scores for all teams at this timestamp
            for t_id, score in team_scores.items():
                team_name = teams.get(id=t_id).name
                score_data[timestamp][team_name] = score
        else:
            # Just update this team's score
            team_name = teams.get(id=team_id).name
            score_data[timestamp][team_name] = team_scores[team_id]

    # If no submissions exist or not enough data points, create sample data
    if len(score_data) < 2:
        # Add initial point at event start (0 scores)
        score_data[0] = {team.name: 0 for team in teams}

        # Add current point at "now" with current scores
        now_timestamp = int((datetime.datetime.now() - event_start).total_seconds())
        score_data[now_timestamp] = {team.name: team.score for team in teams}

    # Convert to JSON
    return json.dumps(score_data)


def generate_user_score_graph_data(users, event):
    """
    Generate JSON data for user score progression graph.
    """
    import json
    from django.db.models import Sum, Count
    from challenges.models import Submission
    import datetime

    # Dictionary to store score progression data
    score_data = {}
    
    # Get all correct submissions ordered by timestamp
    submissions = Submission.objects.filter(
        user__isnull=False,
        team__isnull=True,  # Only individual submissions
        is_correct=True,
        challenge__event=event
    ).order_by('submitted_at')
    
    # Track each user's score over time
    user_scores = {user.id: 0 for user in users}
    
    # Get the event start time for timestamp calculation
    event_start = event.start_time if event and event.start_time else submissions.first().submitted_at if submissions.exists() else datetime.datetime.now()
    
    # Generate timestamps and scores
    for submission in submissions:
        # Skip if not a user submission
        if not submission.user:
            continue
            
        # Update user's score
        user_id = submission.user.id
        user_scores[user_id] += submission.challenge.value
        
        # Calculate timestamp in seconds since event start
        timestamp = int((submission.submitted_at - event_start).total_seconds())
        
        # Ensure timestamp exists in the data
        if timestamp not in score_data:
            score_data[timestamp] = {}
            
            # Add current scores for all users at this timestamp
            for u_id, score in user_scores.items():
                user_name = users.get(id=u_id).username
                score_data[timestamp][user_name] = score
        else:
            # Just update this user's score
            user_name = users.get(id=user_id).username
            score_data[timestamp][user_name] = user_scores[user_id]
    
    # If no submissions exist or not enough data points, create sample data
    if len(score_data) < 2:
        # Add initial point at event start (0 scores)
        score_data[0] = {user.username: 0 for user in users}
        
        # Add current point at "now" with current scores
        now_timestamp = int((datetime.datetime.now() - event_start).total_seconds())
        score_data[now_timestamp] = {user.username: user.score for user in users if hasattr(user, 'score')}
    
    # Convert to JSON
    return json.dumps(score_data)


@login_required
def notifications(request):
    """
    User notifications page.
    """
    # This would typically connect to a notifications model
    # For now, just render an empty notifications page
    
    context = {
        'notifications': [],
    }
    
    return render(request, 'core/notifications.html', context)

def rules(request):
    """
    CTF rules page.
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()

    if not current_event:
        messages.error(request, _('No active CTF event is currently available.'))
        return redirect('core:home')

    # Using the description field since there's no dedicated rules field
    rules_content = current_event.description or _(
        "No rules have been specified for this event."
    )

    context = {
        "event": current_event,
        "rules": rules_content,
    }

    return render(request, 'core/rules.html', context)

def faq(request):
    """
    Frequently asked questions page.
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()
    
    context = {
        'event': current_event,
        'faq': current_event.faq if current_event else None,
    }
    
    return render(request, 'core/faq.html', context)

def privacy(request):
    """
    Privacy policy page.
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()
    
    context = {
        'event': current_event,
        'privacy_policy': current_event.privacy_policy if current_event else None,
    }
    
    return render(request, 'core/privacy.html', context)

def about(request):
    """
    About page.
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()

    context = {
        "event": current_event,
    }
    return render(request, "core/about.html", context)


@login_required
def notifications(request):
    """
    User notifications page/API.
    GET: Return notifications page
    POST: Mark notifications as read
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()

    # Get all user notifications, newest first
    user_notifications = Notification.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    # If AJAX request, return JSON data
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # Return only recent unread notifications for AJAX requests
        unread_notifications = NotificationService.get_pending_notifications(
            request.user
        )

        notifications_data = []
        for notification in unread_notifications:
            display_type = (
                notification.metadata.get("display_type", "toast")
                if notification.metadata
                else "toast"
            )
            sound = (
                notification.metadata.get("sound", "notification")
                if notification.metadata
                else "notification"
            )

            notifications_data.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "created_at": notification.created_at.isoformat(),
                    "link": notification.link,
                    "display_type": display_type,
                    "sound": sound,
                }
            )

        return JsonResponse(
            {"notifications": notifications_data, "count": len(notifications_data)}
        )

    # Handle POST request (mark notifications as read)
    if request.method == "POST":
        notification_id = request.POST.get("notification_id")
        mark_all = request.POST.get("mark_all")

        if mark_all:
            # Mark all as read
            count = NotificationService.mark_all_as_read(request.user)
            messages.success(request, f"{count} notifications marked as read.")
        elif notification_id:
            # Mark specific notification as read
            try:
                notification = Notification.objects.get(
                    id=notification_id, user=request.user
                )
                notification.mark_as_read()
                messages.success(request, "Notification marked as read.")
            except Notification.DoesNotExist:
                messages.error(request, "Notification not found.")

        # Redirect back to notifications page
        return redirect("core:notifications")

    context = {
        "event": current_event,
        "notifications": user_notifications,
        "unread_count": user_notifications.filter(is_read=False).count(),
    }
    return render(request, "core/notifications.html", context)


def is_organizer_or_admin(user):
    """
    Check if user is an organizer or admin.
    """
    return user.is_authenticated and (
        user.type in ["admin", "organizer"] or user.is_superuser
    )


@login_required
@user_passes_test(is_organizer_or_admin)
def notification_manager(request):
    """
    Notification management page for organizers and admins.
    """
    # Get current event
    current_event = Event.objects.filter(is_visible=True).first()

    # Get active events for the dropdown
    active_events = Event.objects.filter(status__in=["running", "upcoming"]).order_by(
        "name"
    )

    context = {
        "event": current_event,
        "active_events": active_events,
        "notification_types": NotificationService.NOTIFICATION_TYPES,
        "display_types": NotificationService.DISPLAY_TYPES,
        "sound_options": NotificationService.SOUND_OPTIONS,
    }
    return render(request, "core/notification_manager.html", context)


@login_required
@user_passes_test(is_organizer_or_admin)
@require_POST
def send_notification(request):
    """
    API endpoint to send a notification.
    """
    # Get form data
    title = request.POST.get("title")
    message = request.POST.get("message")
    notification_type = request.POST.get("notification_type", "system")
    display_type = request.POST.get("display_type", "toast")
    sound = request.POST.get("sound", "notification")
    link = request.POST.get("link")
    target = request.POST.get("target", "all")  # all, event, user
    event_id = request.POST.get("event_id")
    user_id = request.POST.get("user_id")
    scheduled = request.POST.get("scheduled", "false") == "true"
    scheduled_date = request.POST.get("scheduled_date")
    scheduled_time = request.POST.get("scheduled_time")

    # Validate required fields
    if not title or not message:
        messages.error(request, "Title and message are required.")
        return redirect("core:notification_manager")

    # Prepare scheduled_time if needed
    scheduled_datetime = None
    if scheduled and scheduled_date:
        try:
            from datetime import datetime

            # Combine date and time
            if scheduled_time:
                date_time_str = f"{scheduled_date} {scheduled_time}"
                scheduled_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            else:
                scheduled_datetime = datetime.strptime(scheduled_date, "%Y-%m-%d")

            # Convert to timezone aware
            scheduled_datetime = timezone.make_aware(scheduled_datetime)

            # If scheduled time is in the past, show error
            if scheduled_datetime < timezone.now():
                messages.error(request, "Scheduled time cannot be in the past.")
                return redirect("core:notification_manager")
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect("core:notification_manager")

    # Prepare metadata
    metadata = {
        "display_type": display_type,
        "sound": sound,
        "scheduled": scheduled,
    }

    # Get event if specified
    event = None
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
            return redirect("core:notification_manager")

    # Send notification based on target
    if target == "all":
        notifications = NotificationService.send_notification_to_all(
            title=title,
            message=message,
            notification_type=notification_type,
            display_type=display_type,
            sound=sound,
            link=link,
            event=event,
            metadata=metadata,
            scheduled_time=scheduled_datetime,
        )
        messages.success(request, f"Notification sent to {len(notifications)} users.")

    elif target == "event" and event:
        notifications = NotificationService.send_notification_to_event(
            event=event,
            title=title,
            message=message,
            notification_type=notification_type,
            display_type=display_type,
            sound=sound,
            link=link,
            metadata=metadata,
            scheduled_time=scheduled_datetime,
        )
        messages.success(
            request, f"Notification sent to {len(notifications)} event participants."
        )

    elif target == "user" and user_id:
        try:
            user = BaseUser.objects.get(id=user_id)
            NotificationService.send_notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                display_type=display_type,
                sound=sound,
                link=link,
                event=event,
                metadata=metadata,
                scheduled_time=scheduled_datetime,
            )
            messages.success(request, f"Notification sent to {user.username}.")
        except BaseUser.DoesNotExist:
            messages.error(request, "User not found.")

    else:
        messages.error(request, "Invalid target or missing required information.")

    return redirect("core:notification_manager")
