"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Sum, Case, When, IntegerField
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse

from .models import Team, TeamInvite
from users.models import BaseUser
from challenges.models import Submission
from utils.country_code import COUNTRY_CHOICES

@login_required
def manage_team(request):
    """
    Team management page for team captains.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    if request.user != request.user.team.captain:
        messages.error(request, _('Only team captains can access the team management page.'))
        return redirect('teams:profile')
    
    # Get pending invites
    pending_invites = TeamInvite.objects.filter(team=request.user.team, status='pending')
    
    context = {
        'team': request.user.team,
        'pending_invites': pending_invites,
        'country_choices': COUNTRY_CHOICES,
    }
    
    return render(request, 'teams/manage.html', context)

@login_required
@require_http_methods(["POST"])
def promote_captain(request):
    """
    Promote a team member to team captain.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    team = request.user.team
    if request.user != team.captain:
        messages.error(request, _('Only team captains can promote members.'))
        return redirect('teams:profile')
    
    # Get the user to promote
    try:
        user_id = request.POST.get('user_id')
        new_captain = BaseUser.objects.get(id=user_id)
    except (ValueError, BaseUser.DoesNotExist):
        messages.error(request, _('Invalid user selected.'))
        return redirect('teams:manage')
    
    # Check if user is in the team
    if new_captain.team != team:
        messages.error(request, _('Selected user is not a member of your team.'))
        return redirect('teams:manage')
    
    # Promote user to captain
    team.captain = new_captain
    team.save()
    
    messages.success(request, _(f'{new_captain.username} has been promoted to team captain.'))
    return redirect('teams:profile')

@login_required
@require_http_methods(["POST"])
def change_team_password(request):
    """
    Change the team password.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    team = request.user.team
    if request.user != team.captain:
        messages.error(request, _('Only team captains can change the team password.'))
        return redirect('teams:profile')
    
    # Update password
    password = request.POST.get('password')
    if not password:
        messages.error(request, _('Password cannot be empty.'))
        return redirect('teams:manage')
    
    team.password = password
    team.save()
    
    messages.success(request, _('Team password has been updated.'))
    return redirect('teams:manage')

@login_required
@require_http_methods(["POST"])
def team_settings(request):
    """
    Update team settings.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    team = request.user.team
    if request.user != team.captain:
        messages.error(request, _('Only team captains can change team settings.'))
        return redirect('teams:profile')
    
    # Update settings
    visibility = request.POST.get('visibility') == 'on'
    join_mode = 'open' if request.POST.get('join_mode') == 'on' else 'invite'
    
    team.visibility = visibility
    team.join_mode = join_mode
    team.save()
    
    messages.success(request, _('Team settings have been updated.'))
    return redirect('teams:manage')

@login_required
@require_http_methods(["POST"])
def cancel_invite(request, invite_id):
    """
    Cancel a pending team invitation.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    team = request.user.team
    if request.user != team.captain:
        messages.error(request, _('Only team captains can cancel invitations.'))
        return redirect('teams:profile')
    
    # Get the invite
    invite = get_object_or_404(TeamInvite, id=invite_id, team=team)
    
    # Cancel the invite
    invite.status = 'cancelled'
    invite.save()
    
    messages.success(request, _('Invitation has been cancelled.'))
    return redirect('teams:manage')

@login_required
@require_http_methods(["POST"])
def dissolve_team(request):
    """
    Dissolve the team and remove all members.
    """
    # Check if user is in a team
    if not request.user.team:
        messages.error(request, _('You are not part of a team.'))
        return redirect('teams:create')
    
    # Check if user is team captain
    team = request.user.team
    if request.user != team.captain:
        messages.error(request, _('Only team captains can dissolve the team.'))
        return redirect('teams:profile')
    
    # Get all members
    members = list(team.members.all())
    
    # Remove all members from the team
    for member in members:
        member.team = None
        member.save()
    
    # Delete the team
    team_name = team.name
    team.delete()
    
    messages.success(request, _(f'Team "{team_name}" has been dissolved.'))
    return redirect('core:home')
