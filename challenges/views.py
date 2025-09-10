"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, FileResponse
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .models import Challenge, ChallengeCategory, Submission, Hint, File, HintUnlock
from teams.models import Team
from event.models import Event

@login_required
def challenge_list(request):
    """
    Display a list of all available challenges.
    """
    # Get the current event - we'll use it for display purposes only
    current_event = Event.objects.filter(is_visible=True).first()

    if not current_event:
        # Create a default event if none exists
        from django.utils.text import slugify
        current_event = Event.objects.create(
            name=settings.EVENT_NAME,
            slug=slugify(settings.EVENT_NAME),
            description=f"{settings.EVENT_NAME} CTF Event",
            short_description=f"{settings.EVENT_NAME} CTF Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            registration_start=timezone.now(),
            registration_end=timezone.now() + timezone.timedelta(days=30),
            status='running',
            is_visible=True
        )

    # Get all challenge categories
    categories = ChallengeCategory.objects.all()

    # Get all challenges visible to the user - ignore event filtering
    visible_challenges = Challenge.objects.filter(is_visible=True)

    # Get total challenges count
    total_challenges = visible_challenges.count()

    # Get total possible points
    total_points = visible_challenges.aggregate(Sum("value"))["value__sum"] or 0

    # Get user's solved challenges and points earned
    if request.user.is_authenticated:
        team = getattr(request.user, 'team', None)
        if team:
            solved_challenges = Submission.objects.filter(
                team=team, 
                is_correct=True,
                challenge__in=visible_challenges
            ).values_list('challenge_id', flat=True)

            earned_points = (
                visible_challenges.filter(id__in=solved_challenges).aggregate(
                    Sum("value")
                )["value__sum"]
                or 0
            )

        else:
            solved_challenges = Submission.objects.filter(
                user=request.user, 
                is_correct=True,
                challenge__in=visible_challenges
            ).values_list('challenge_id', flat=True)

            earned_points = (
                visible_challenges.filter(id__in=solved_challenges).aggregate(
                    Sum("value")
                )["value__sum"]
                or 0
            )
    else:
        solved_challenges = []
        earned_points = 0

    # Annotate challenges with solve count
    challenges_with_solves = visible_challenges.annotate(
        solves=Count("submissions", filter=Q(submissions__is_correct=True))
    )

    # Check prerequisite status for each challenge
    prerequisite_status = {}
    for challenge in challenges_with_solves:
        prerequisite_status[challenge.id] = challenge.check_prerequisites_met(
            request.user
        )

    context = {
        "event": current_event,
        "categories": categories,
        "challenges": challenges_with_solves,
        "solved_challenges": solved_challenges,
        "total_challenges": total_challenges,
        "total_points": total_points,
        "earned_points": earned_points,
        "now": timezone.now(),
        "prerequisite_status": prerequisite_status,
    }

    return render(request, 'challenges/list.html', context)

@login_required
def challenge_detail(request, challenge_id):
    """
    Display details of a specific challenge.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id, is_visible=True)

    # Check if the CTF has started
    current_event = Event.objects.filter(is_visible=True, start_time__lte=timezone.now()).first()

    if not current_event or challenge.event != current_event:
        messages.error(request, _('This challenge is not available.'))
        return redirect('challenges:list')

    # Check if prerequisites are met
    prerequisites_met = challenge.check_prerequisites_met(request.user)
    if not prerequisites_met:
        messages.error(
            request, _("You need to solve the prerequisite challenges first.")
        )
        return redirect("challenges:list")

    # Check if the CTF has ended
    if current_event.end_time and current_event.end_time < timezone.now():
        messages.info(request, _('This CTF event has ended.'))

    # Get hints for this challenge
    hints = Hint.objects.filter(challenge=challenge).order_by('position')

    # Get the user's unlocked hints
    unlocked_hints = []
    team = getattr(request.user, "team", None)

    # Get hints unlocked by this user or team
    try:
        from .models import HintUnlock

        if team:
            # Get hints unlocked by this team
            hint_unlocks = HintUnlock.objects.filter(
                team=team, hint__challenge=challenge
            )
        else:
            # Get hints unlocked by this user
            hint_unlocks = HintUnlock.objects.filter(
                user=request.user, hint__challenge=challenge
            )

        unlocked_hints = [unlock.hint.id for unlock in hint_unlocks]
    except:
        # For demonstration, unlock all hints
        unlocked_hints = [hint.id for hint in hints]

    # Get files for this challenge
    files = File.objects.filter(challenge=challenge)

    # Check if the user/team has solved this challenge
    team = getattr(request.user, 'team', None)
    if team:
        solved = Submission.objects.filter(
            team=team, 
            challenge=challenge,
            is_correct=True
        ).exists()
    else:
        solved = Submission.objects.filter(
            user=request.user, 
            challenge=challenge,
            is_correct=True
        ).exists()

    # Get user/team submissions for this challenge
    if team:
        submissions = Submission.objects.filter(
            team=team, 
            challenge=challenge
        ).order_by('-submitted_at')
    else:
        submissions = Submission.objects.filter(
            user=request.user, 
            challenge=challenge
        ).order_by('-submitted_at')

    # Get the list of solvers for this challenge
    solvers = []
    if challenge.type == "team":
        correct_submissions = (
            Submission.objects.filter(challenge=challenge, is_correct=True)
            .select_related("team", "user")
            .order_by("submitted_at")
        )

        for submission in correct_submissions:
            if submission.team and submission.team not in [
                s.get("team") for s in solvers if s.get("team")
            ]:
                solvers.append(
                    {
                        "team": submission.team,
                        "name": submission.team.name,
                        "time": submission.submitted_at,
                        "is_team": True,
                    }
                )
    else:
        correct_submissions = (
            Submission.objects.filter(challenge=challenge, is_correct=True)
            .select_related("user")
            .order_by("submitted_at")
        )

        for submission in correct_submissions:
            if submission.user and submission.user not in [
                s.get("user") for s in solvers if s.get("user")
            ]:
                solvers.append(
                    {
                        "user": submission.user,
                        "name": submission.user.username,
                        "time": submission.submitted_at,
                        "is_team": False,
                    }
                )

    # Calculate solve statistics
    solves_count = len(solvers)
    attempts_count = Submission.objects.filter(challenge=challenge).count()
    solve_percentage = (
        round((solves_count / attempts_count) * 100) if attempts_count > 0 else 0
    )
    first_blood = solvers[0] if solvers else None
    first_blood_time = first_blood["time"].strftime("%H:%M:%S") if first_blood else None

    context = {
        "challenge": challenge,
        "hints": hints,
        "unlocked_hints": unlocked_hints,
        "files": files,
        "solved": solved,
        "submissions": submissions,
        "solvers": solvers,
        "solves_count": solves_count,
        "attempts_count": attempts_count,
        "solve_percentage": solve_percentage,
        "first_blood": first_blood,
        "first_blood_time": first_blood_time,
        "prerequisites": challenge.prerequisites.all(),
    }

    return render(request, 'challenges/detail.html', context)

@login_required
@require_http_methods(["POST"])
def submit_flag(request, challenge_id):
    """
    Handle flag submission for a challenge.
    """
    challenge = get_object_or_404(Challenge, pk=challenge_id, is_visible=True)
    flag = request.POST.get('flag', '').strip()

    if not flag:
        return JsonResponse({'status': 'error', 'message': _('Please enter a flag.')})

    # Check if the CTF has ended
    current_event = Event.objects.filter(is_visible=True).first()
    if current_event.end_time and current_event.end_time < timezone.now():
        return JsonResponse({'status': 'error', 'message': _('This CTF event has ended.')})

    # Check if prerequisites are met
    prerequisites_met = challenge.check_prerequisites_met(request.user)
    if not prerequisites_met:
        return JsonResponse(
            {
                "status": "error",
                "message": _("You need to solve the prerequisite challenges first."),
            }
        )

    # Check if the user/team has already solved this challenge
    team = getattr(request.user, 'team', None)
    if team:
        already_solved = Submission.objects.filter(
            team=team, 
            challenge=challenge,
            is_correct=True
        ).exists()
    else:
        already_solved = Submission.objects.filter(
            user=request.user, 
            challenge=challenge,
            is_correct=True
        ).exists()

    if already_solved:
        return JsonResponse({'status': 'error', 'message': _('You have already solved this challenge.')})

    # Check if the flag is correct
    is_correct = challenge.check_flag(flag)

    # Create submission record
    submission = Submission(
        user=request.user,
        team=team,
        challenge=challenge,
        flag_submitted=flag,
        is_correct=is_correct
    )
    submission.save()

    if is_correct:
        # Calculate points
        points = challenge.value

        # Update user/team score
        if team:
            team.score += points
            team.last_score_update = timezone.now()
            team.save()
        else:
            request.user.score += points
            request.user.last_score_update = timezone.now()
            request.user.save()

        return JsonResponse({
            'status': 'success', 
            'message': _('Correct flag! You earned {} points.').format(points)
        })
    else:
        return JsonResponse({
            'status': 'error', 
            'message': _('Incorrect flag. Please try again.')
        })

@login_required
def unlock_hint(request, hint_id):
    """
    Unlock a hint for a challenge.
    """
    hint = get_object_or_404(Hint, pk=hint_id)

    # Check if the hint is already unlocked
    team = getattr(request.user, 'team', None)
    if team:
        already_unlocked = HintUnlock.objects.filter(hint=hint, team=team).exists()
    else:
        already_unlocked = HintUnlock.objects.filter(
            hint=hint, user=request.user
        ).exists()

    if already_unlocked:
        return JsonResponse({'status': 'success', 'hint': hint.content})

    # Check if user/team has enough points to unlock the hint
    cost = hint.cost
    if team:
        current_points = team.score
    else:
        current_points = request.user.score

    if current_points < cost:
        return JsonResponse({
            'status': 'error', 
            'message': _('Not enough points to unlock this hint. You need {} points.').format(cost)
        })

    # Deduct points and unlock the hint
    if team:
        team.score -= cost
        team.save()
        # Create hint unlock record
        HintUnlock.objects.create(hint=hint, user=request.user, team=team, cost=cost)
    else:
        request.user.score -= cost
        request.user.save()
        # Create hint unlock record
        HintUnlock.objects.create(hint=hint, user=request.user, cost=cost)

    return JsonResponse({'status': 'success', 'hint': hint.content})

@login_required
def download_file(request, file_id):
    """
    Download a challenge file.
    """
    file = get_object_or_404(File, pk=file_id)
    
    # Check if the user has access to this file
    challenge = file.challenge
    if not challenge.is_visible:
        return HttpResponseForbidden(_('You do not have access to this file.'))
    
    # Serve the file
    response = FileResponse(file.file)
    response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
    return response
