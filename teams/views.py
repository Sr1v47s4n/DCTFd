"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings

from .models import Team, TeamInvite
from users.models import BaseUser
from event.models import Event
from challenges.models import Submission
from .forms import TeamCreationForm, TeamJoinForm, TeamProfileUpdateForm
from utils.country_code import COUNTRY_CHOICES

# Import team management functions
from .team_management import (
    manage_team,
    promote_captain,
    change_team_password,
    team_settings,
    cancel_invite,
    dissolve_team,
)

@login_required
def teams_list(request):
    """
    Display a list of all teams.
    """
    # Get the current event
    current_event = Event.objects.filter(is_visible=True).first()

    if not current_event:
        messages.error(request, _('No active CTF event is currently available.'))
        return redirect('core:home')

    # Get all teams
    teams = Team.objects.all().order_by("-score")

    # Paginate the teams
    paginator = Paginator(teams, 25)  # 25 teams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request, 'teams/list.html', context)

@login_required
def create_team(request):
    """
    Create a new team.
    """
    # Get the current event
    current_event = Event.objects.filter(is_visible=True).first()

    if not current_event:
        messages.error(request, _('No active CTF event is currently available.'))
        return redirect('core:home')

    # Check if user is already in a team
    if hasattr(request.user, 'team') and request.user.team:
        messages.error(request, _('You are already in a team.'))
        return redirect('teams:profile')

    # Get custom field definitions if enabled
    custom_field_definitions = []
    if current_event:
        try:
            event_settings = current_event.settings
            if hasattr(event_settings, "enable_team_custom_fields") and event_settings.enable_team_custom_fields:
                from django.contrib.contenttypes.models import ContentType
                from core.custom_fields import CustomFieldDefinition

                event_content_type = ContentType.objects.get_for_model(Event)
                custom_field_definitions = CustomFieldDefinition.objects.filter(
                    content_type=event_content_type,
                    object_id=current_event.id,
                    field_for="team"
                ).order_by('order')
        except:
            pass

    if request.method == 'POST':
        form = TeamCreationForm(request.POST, request.FILES)

        # Process custom fields
        custom_fields_data = {}
        for field in custom_field_definitions:
            field_id = str(field.id)
            if field.field_type == 'checkbox':
                # Handle multiple values for checkboxes
                values = request.POST.getlist(f'custom_fields[{field_id}][]', [])
                if values:
                    custom_fields_data[field_id] = values
            else:
                # Handle single value for other field types
                value = request.POST.get(f'custom_fields[{field_id}]', '')
                if value:
                    custom_fields_data[field_id] = value

        if form.is_valid():
            team = form.save(commit=False)
            team.captain = request.user
            team.save()

            # Add the user to the team
            request.user.team = team
            request.user.save()

        # Save custom fields
        if custom_field_definitions and custom_fields_data:
            from django.contrib.contenttypes.models import ContentType
            from core.custom_fields import CustomFieldValue

            team_content_type = ContentType.objects.get_for_model(Team)

            for field_def in custom_field_definitions:
                field_id = str(field_def.id)
                if field_id in custom_fields_data:
                    value = custom_fields_data[field_id]

                    # Convert list values to JSON for checkbox fields
                    if isinstance(value, list):
                        import json
                        value = json.dumps(value)

                    # Save the custom field value
                    CustomFieldValue.objects.create(
                        field_definition=field_def,
                        content_type=team_content_type,
                        object_id=team.id,
                        value=value
                    )

        messages.success(request, _('Team created successfully!'))
        return redirect('teams:profile')

    # Render the form
    form = TeamCreationForm()
    context = {"form": form, "custom_field_definitions": custom_field_definitions}
    return render(request, 'teams/create.html', context)

@login_required
def join_team(request):
    """
    Join an existing team.
    """
    # Check if user is already in a team
    if hasattr(request.user, 'team') and request.user.team:
        messages.error(request, _('You are already in a team.'))
        return redirect('teams:profile')
    
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        team_password = request.POST.get('team_password')
        
        if not team_name or not team_password:
            messages.error(request, _('Team name and password are required.'))
            return render(request, 'teams/join.html')
        
        # Get the current event
        current_event = Event.objects.filter(is_visible=True).first()
        
        if not current_event:
            messages.error(request, _('No active CTF event is currently available.'))
            return redirect('core:home')
        
        # Find the team
        try:
            team = Team.objects.get(name=team_name, event=current_event)
        except Team.DoesNotExist:
            messages.error(request, _('Team not found.'))
            return render(request, 'teams/join.html')
        
        # Check team password
        if not team.check_password(team_password):
            messages.error(request, _('Incorrect team password.'))
            return render(request, 'teams/join.html')
        
        # Check if team is full
        members_count = BaseUser.objects.filter(team=team).count()
        if members_count >= current_event.team_size:
            messages.error(request, _('This team is full.'))
            return render(request, 'teams/join.html')
        
        # Join the team
        request.user.team = team
        request.user.save()
        
        messages.success(request, _('You have joined the team successfully!'))
        return redirect('teams:profile')
    
    return render(request, 'teams/join.html')

@login_required
def team_profile(request):
    """
    Display the user's team profile.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team. Create or join a team first.'))
        return redirect('teams:list')
    
    team = request.user.team
    
    # Get team members
    members = BaseUser.objects.filter(team=team)
    
    # Get team stats
    solved_challenges = Submission.objects.filter(
        team=team,
        is_correct=True
    ).values_list('challenge_id', flat=True).distinct()
    
    context = {
        'team': team,
        'members': members,
        'is_captain': request.user == team.captain,
        'solved_challenges': solved_challenges,
    }
    
    return render(request, 'teams/profile.html', context)

@login_required
def edit_team_profile(request):
    """
    Edit team profile.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team. Create or join a team first.'))
        return redirect('teams:list')

    team = request.user.team

    # Check if user is team captain
    if request.user != team.captain:
        messages.error(request, _('Only the team captain can edit the team profile.'))
        return redirect('teams:profile')

    if request.method == 'POST':
        form = TeamProfileUpdateForm(request.POST, request.FILES, instance=team)

        import time

        print("=" * 80)
        print(f"[DEBUG] TEAM PROFILE EDIT POST REQUEST RECEIVED - {time.time()}")
        print(f"[DEBUG] POST Data: {request.POST}")
        print(f"[DEBUG] FILES Data: {request.FILES}")

        old_avatar_id = team.avatar.id if team.avatar else None
        print(f"[DEBUG] Old Avatar ID: {old_avatar_id}")
        print(f"[DEBUG] Current Team Avatar URL: {team.get_avatar_url()}")

        # Track if any avatar changes were made
        avatar_updated = False

        # Handle logo file upload first (highest priority)
        if "logo" in request.FILES:
            logo = request.FILES["logo"]
            print(f"[DEBUG] Custom logo file detected: {logo.name}")

            # Clear any previous avatar selection when uploading custom logo
            team.avatar = None
            team.logo = logo
            team.save(update_fields=["avatar", "logo"])

            print(f"[DEBUG] Custom logo file saved and set as primary avatar")
            messages.success(
                request, "Custom logo has been uploaded and set as your team avatar."
            )
            avatar_updated = True

        # Then handle predefined avatar selection (if no custom logo was uploaded)
        elif "avatar" in request.POST and request.POST.get("avatar"):
            selected_avatar_id = request.POST.get("avatar")
            print(f"[DEBUG] Selected Avatar ID from POST: {selected_avatar_id}")

            from users.avatar_models import AvatarOption

            try:
                avatar = AvatarOption.objects.get(id=selected_avatar_id)
                print(f"[DEBUG] Found avatar object: {avatar.id} - {avatar.name}")

                # Update avatar directly in the database
                team.avatar = avatar
                # Clear any custom logo when selecting a predefined one
                team.logo = None
                team.save(update_fields=["avatar", "logo"])

                print(f"[DEBUG] Avatar updated directly: {avatar.id} - {avatar.name}")
                messages.success(
                    request, f'Avatar has been updated to "{avatar.name}".'
                )
                avatar_updated = True
            except AvatarOption.DoesNotExist:
                print(f"[DEBUG] ERROR: Avatar with ID {selected_avatar_id} not found!")
                messages.error(request, "Selected avatar not found.")

        # Force reload team to get updated avatar
        if avatar_updated:
            team.refresh_from_db()
            print(f"[DEBUG] After avatar update. Avatar URL: {team.get_avatar_url()}")

            # Update the instance used by the form
            form = TeamProfileUpdateForm(request.POST, request.FILES, instance=team)

        # Now validate the form for other fields
        print(f"[DEBUG] Form is valid: {form.is_valid()}")
        if form.is_valid():
            form.save()
            messages.success(request, _("Team profile updated successfully!"))
            return redirect("teams:profile")
        else:
            print(f"[DEBUG] Form errors: {form.errors}")
            messages.error(request, _("Please correct the errors below."))
    else:
        form = TeamProfileUpdateForm(instance=team)

    context = {
        "team": team,
        "form": form,
    }

    return render(request, 'teams/edit_profile.html', context)

    return render(request, "teams/edit_profile.html", context)

@login_required
def team_members(request):
    """
    Manage team members.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team. Create or join a team first.'))
        return redirect('teams:list')
    
    team = request.user.team
    
    # Get team members
    members = BaseUser.objects.filter(team=team)
    
    # Get pending invites
    if request.user == team.captain:
        pending_invites = TeamInvite.objects.filter(team=team, status='pending')
    else:
        pending_invites = []
    
    context = {
        'team': team,
        'members': members,
        'pending_invites': pending_invites,
        'is_captain': request.user == team.captain,
    }
    
    return render(request, 'teams/members.html', context)

@login_required
def invite_member(request):
    """
    Invite a user to join the team.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team. Create or join a team first.'))
        return redirect('teams:list')
    
    team = request.user.team
    
    # Check if user is team captain
    if request.user != team.captain:
        messages.error(request, _('Only the team captain can invite members.'))
        return redirect('teams:members')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        
        if not username:
            messages.error(request, _('Username is required.'))
            return redirect('teams:members')
        
        # Find the user
        try:
            user = BaseUser.objects.get(username=username)
        except BaseUser.DoesNotExist:
            messages.error(request, _('User not found.'))
            return redirect('teams:members')
        
        # Check if user is already in a team
        if hasattr(user, 'team') and user.team:
            messages.error(request, _('This user is already in a team.'))
            return redirect('teams:members')
        
        # Check if an invite already exists
        if TeamInvite.objects.filter(team=team, user=user, status='pending').exists():
            messages.error(request, _('An invite already exists for this user.'))
            return redirect('teams:members')
        
        # Create the invite
        invite = TeamInvite(
            team=team,
            user=user,
            created_by=request.user
        )
        invite.save()
        
        messages.success(request, _('Invite sent successfully!'))
        return redirect('teams:members')
    
    return redirect('teams:members')

@login_required
def kick_member(request, user_id):
    """
    Remove a member from the team.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team. Create or join a team first.'))
        return redirect('teams:list')
    
    team = request.user.team
    
    # Check if user is team captain
    if request.user != team.captain:
        messages.error(request, _('Only the team captain can remove members.'))
        return redirect('teams:members')
    
    # Find the user to kick
    user_to_kick = get_object_or_404(BaseUser, pk=user_id, team=team)
    
    # Cannot kick yourself
    if user_to_kick == request.user:
        messages.error(request, _('You cannot remove yourself from the team.'))
        return redirect('teams:members')
    
    # Remove from team
    user_to_kick.team = None
    user_to_kick.save()
    
    messages.success(request, _('Member removed successfully!'))
    return redirect('teams:members')

@login_required
def leave_team(request):
    """
    Leave the current team.
    """
    # Check if user is in a team
    if not hasattr(request.user, 'team') or not request.user.team:
        messages.info(request, _('You are not in a team.'))
        return redirect('teams:list')
    
    team = request.user.team
    
    # If the user is the captain, check if there are other members
    if request.user == team.captain:
        other_members = BaseUser.objects.filter(team=team).exclude(pk=request.user.pk)
        
        if other_members.exists():
            # Transfer captainship to another member
            new_captain = other_members.first()
            team.captain = new_captain
            team.save()
        else:
            # If no other members, delete the team
            team.delete()
            request.user.team = None
            request.user.save()
            messages.success(request, _('You have left the team and it has been disbanded.'))
            return redirect('teams:list')
    
    # Leave the team
    request.user.team = None
    request.user.save()
    
    messages.success(request, _('You have left the team.'))
    return redirect('teams:list')

def public_team_profile(request, team_id):
    """
    View a team's public profile.
    """
    team = get_object_or_404(Team, pk=team_id)

    # Get team members
    members = BaseUser.objects.filter(team=team)

    # Get team stats - fetch complete challenge objects instead of just IDs
    from challenges.models import Challenge

    solved_challenge_ids = (
        Submission.objects.filter(team=team, is_correct=True)
        .values_list("challenge_id", flat=True)
        .distinct()
    )

    solved_challenges = Challenge.objects.filter(id__in=solved_challenge_ids)

    context = {
        'team': team,
        'members': members,
        'solved_challenges': solved_challenges,
    }

    return render(request, 'teams/public_profile.html', context)
