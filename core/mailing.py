"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import os
import logging
from typing import List, Dict, Any, Union, Optional
from smtplib import SMTPException

from dotenv import load_dotenv
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

load_dotenv()

logger = logging.getLogger(__name__)


class EmailSender:
    """
    Utility class to handle all email operations in the application.
    This centralizes email sending logic for different types of notifications.
    """
    
    @staticmethod
    def send_email(
        subject: str,
        recipient_list: List[str],
        html_message: str,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
        plain_message: Optional[str] = None,
        **kwargs
    ) -> bool:
        """
        Send an email with both HTML and plain text versions.
        
        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            html_message: HTML content of the email
            from_email: Sender email address (default: settings.DEFAULT_FROM_EMAIL)
            fail_silently: Whether to suppress email sending exceptions
            plain_message: Plain text version (auto-generated from HTML if not provided)
            **kwargs: Additional arguments to pass to EmailMultiAlternatives
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not from_email:
                from_email = settings.DEFAULT_FROM_EMAIL
                
            if not plain_message:
                plain_message = strip_tags(html_message)
                
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=from_email,
                to=recipient_list,
                **kwargs
            )
            
            email.attach_alternative(html_message, "text/html")
            return email.send() > 0
            
        except SMTPException as e:
            logger.error(f"Failed to send email: {str(e)}")
            if not fail_silently:
                raise
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            if not fail_silently:
                raise
            return False
    
    @classmethod
    def send_template_email(
        cls,
        subject: str,
        recipient_list: List[str],
        template_name: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
        **kwargs
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            template_name: Path to the template
            context: Context data for the template
            from_email: Sender email address
            fail_silently: Whether to suppress email sending exceptions
            **kwargs: Additional arguments to pass to send_email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        html_message = render_to_string(template_name, context)
        return cls.send_email(
            subject=subject,
            recipient_list=recipient_list,
            html_message=html_message,
            from_email=from_email,
            fail_silently=fail_silently,
            **kwargs
        )


class UserEmailService:
    """
    Service to handle user-related emails such as:
    - Account activation
    - Password reset
    - Email verification
    - Welcome emails
    - Account notifications
    """
    
    @classmethod
    def send_account_activation_email(cls, user, domain, protocol='http'):
        """
        Send account activation email with verification link.
        
        Args:
            user: User model instance
            domain: Domain name for the activation link
            protocol: Protocol to use (http/https)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        from users.tokens import account_activation_token
        
        context = {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': protocol,
        }
        
        return EmailSender.send_template_email(
            subject='Activate Your DCTFd Account',
            recipient_list=[user.email],
            template_name='users/activation_email.html',
            context=context,
        )
    
    @classmethod
    def send_password_reset_email(cls, user, domain, protocol='http'):
        """
        Send password reset email with reset link.
        
        Args:
            user: User model instance
            domain: Domain name for the reset link
            protocol: Protocol to use (http/https)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        from django.contrib.auth.tokens import default_token_generator
        
        context = {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': protocol,
        }
        
        return EmailSender.send_template_email(
            subject='Reset Your DCTFd Password',
            recipient_list=[user.email],
            template_name='users/password_reset_email.html',
            context=context,
        )
    
    @classmethod
    def send_password_changed_email(cls, user):
        """
        Send notification email when password is changed.
        
        Args:
            user: User model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'time': user.last_password_change if hasattr(user, 'last_password_change') else None
        }
        
        return EmailSender.send_template_email(
            subject='Your DCTFd Password Has Been Changed',
            recipient_list=[user.email],
            template_name='users/password_changed_email.html',
            context=context,
        )
    
    @classmethod
    def send_welcome_email(cls, user):
        """
        Send welcome email to new users.
        
        Args:
            user: User model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
        }
        
        return EmailSender.send_template_email(
            subject='Welcome to DCTFd!',
            recipient_list=[user.email],
            template_name='users/welcome_email.html',
            context=context,
        )
    
    @classmethod
    def send_team_invitation_email(cls, inviter, invitee_email, team, token, domain, protocol='http'):
        """
        Send team invitation email.
        
        Args:
            inviter: User who sent the invitation
            invitee_email: Email of the person being invited
            team: Team model instance
            token: Invitation token
            domain: Domain name for the invitation link
            protocol: Protocol to use (http/https)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'inviter': inviter,
            'team': team,
            'domain': domain,
            'token': token,
            'protocol': protocol,
        }
        
        return EmailSender.send_template_email(
            subject=f'Invitation to join team {team.name} on DCTFd',
            recipient_list=[invitee_email],
            template_name='teams/invitation_email.html',
            context=context,
        )
    
    @classmethod
    def send_account_status_email(cls, user, status_type, reason=None):
        """
        Send account status change notification.
        
        Args:
            user: User model instance
            status_type: Type of status change (banned, unbanned, etc.)
            reason: Optional reason for the status change
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'status_type': status_type,
            'reason': reason,
            'timestamp': user.last_active or user.date_joined,
        }
        
        status_titles = {
            'banned': 'Your Account Has Been Suspended',
            'unbanned': 'Your Account Has Been Reactivated',
            'disabled': 'Your Account Has Been Disabled',
            'enabled': 'Your Account Has Been Enabled',
        }
        
        subject = status_titles.get(status_type, f'Account Status Change: {status_type}')
        
        return EmailSender.send_template_email(
            subject=subject,
            recipient_list=[user.email],
            template_name='users/account_status_email.html',
            context=context,
        )
    
    @classmethod
    def send_team_join_confirmation(cls, user, team):
        """
        Send confirmation email when a user joins a team.
        
        Args:
            user: User model instance
            team: Team model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'team': team,
            'is_captain': user.is_team_captain,
        }
        
        return EmailSender.send_template_email(
            subject=f'You Have Joined Team {team.name}',
            recipient_list=[user.email],
            template_name='teams/team_join_confirmation_email.html',
            context=context,
        )
    
    @classmethod
    def send_team_leave_confirmation(cls, user, team_name):
        """
        Send confirmation email when a user leaves a team.
        
        Args:
            user: User model instance
            team_name: Name of the team the user left
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'team_name': team_name,
        }
        
        return EmailSender.send_template_email(
            subject=f'You Have Left Team {team_name}',
            recipient_list=[user.email],
            template_name='teams/team_leave_confirmation_email.html',
            context=context,
        )
    
    @classmethod
    def send_team_member_joined_notification(cls, captain, member, team):
        """
        Notify team captain when a new member joins the team.
        
        Args:
            captain: Team captain user model instance
            member: New team member user model instance
            team: Team model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'captain': captain,
            'member': member,
            'team': team,
        }
        
        return EmailSender.send_template_email(
            subject=f'New Member Joined Team {team.name}',
            recipient_list=[captain.email],
            template_name='teams/team_member_joined_email.html',
            context=context,
        )
    
    @classmethod
    def send_team_member_left_notification(cls, captain, member, team):
        """
        Notify team captain when a member leaves the team.
        
        Args:
            captain: Team captain user model instance
            member: Team member user model instance who left
            team: Team model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'captain': captain,
            'member': member,
            'team': team,
        }
        
        return EmailSender.send_template_email(
            subject=f'Member Left Team {team.name}',
            recipient_list=[captain.email],
            template_name='teams/team_member_left_email.html',
            context=context,
        )


class EventEmailService:
    """
    Service to handle event-related emails such as:
    - Event registration confirmations
    - Event notifications
    - Event updates
    - Announcements
    """
    
    @classmethod
    def send_registration_confirmation_email(cls, user, event):
        """
        Send event registration confirmation email.
        
        Args:
            user: User model instance
            event: Event model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'event': event,
        }
        
        return EmailSender.send_template_email(
            subject=f'Registration Confirmation: {event.name}',
            recipient_list=[user.email],
            template_name='event/registration_confirmation_email.html',
            context=context,
        )
    
    @classmethod
    def send_event_announcement_email(cls, event, announcement, recipient_list=None):
        """
        Send event announcement to all participants.
        
        Args:
            event: Event model instance
            announcement: Announcement content
            recipient_list: Optional list of recipients (if None, sends to all event participants)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if recipient_list is None:
            # Get all participants' emails
            from event.models import EventRegistration
            registrations = EventRegistration.objects.filter(
                event=event, 
                status='approved'
            ).select_related('user')
            recipient_list = [reg.user.email for reg in registrations]
            
        context = {
            'event': event,
            'announcement': announcement,
        }
        
        return EmailSender.send_template_email(
            subject=f'Announcement: {event.name}',
            recipient_list=recipient_list,
            template_name='event/announcement_email.html',
            context=context,
            bcc=recipient_list,  # Use BCC for privacy
            to=[],  # Empty 'to' field when using BCC
        )
    
    @classmethod
    def send_challenge_solved_notification(cls, user, challenge, event):
        """
        Send notification when a user solves a challenge.
        
        Args:
            user: User model instance
            challenge: Challenge model instance
            event: Event model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        context = {
            'user': user,
            'challenge': challenge,
            'event': event,
        }
        
        return EmailSender.send_template_email(
            subject=f'Challenge Solved: {challenge.name}',
            recipient_list=[user.email],
            template_name='challenges/challenge_solved_email.html',
            context=context,
        )


class AdminEmailService:
    """
    Service to handle admin-related emails such as:
    - System notifications
    - Error reports
    - User reports
    """
    
    @classmethod
    def send_new_registration_notification(cls, user):
        """
        Notify admins about new user registrations.
        
        Args:
            user: New user model instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Get admin emails
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_emails = list(User.objects.filter(type='admin', is_active=True).values_list('email', flat=True))
        
        if not admin_emails:
            logger.warning("No admin emails found for notification")
            return False
            
        context = {
            'user': user,
        }
        
        return EmailSender.send_template_email(
            subject='New User Registration',
            recipient_list=admin_emails,
            template_name='admin/new_registration_notification.html',
            context=context,
        )
    
    @classmethod
    def send_profile_update_notification(cls, user):
        """
        Notify admins about user profile updates.
        
        Args:
            user: User model instance that was updated
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Get admin emails
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_emails = list(User.objects.filter(type='admin', is_active=True).values_list('email', flat=True))
        
        if not admin_emails:
            logger.warning("No admin emails found for notification")
            return False
            
        context = {
            'user': user,
        }
        
        return EmailSender.send_template_email(
            subject=f'User Profile Updated: {user.username}',
            recipient_list=admin_emails,
            template_name='admin/profile_update_notification.html',
            context=context,
        )
    
    @classmethod
    def send_error_report_email(cls, error_data, user=None):
        """
        Send error report to admins.
        
        Args:
            error_data: Dictionary containing error details
            user: Optional user who encountered the error
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Get admin emails
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_emails = list(User.objects.filter(type='admin', is_active=True).values_list('email', flat=True))
        
        if not admin_emails:
            logger.warning("No admin emails found for error report")
            return False
            
        context = {
            'error_data': error_data,
            'user': user,
        }
        
        return EmailSender.send_template_email(
            subject='DCTFd Error Report',
            recipient_list=admin_emails,
            template_name='admin/error_report_email.html',
            context=context,
        )

