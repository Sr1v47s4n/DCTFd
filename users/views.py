"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models import Q
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import BaseUser
from teams.models import Team
from .forms import (
    UserRegistrationForm, 
    UserLoginForm, 
    ProfileUpdateForm,
    PasswordResetRequestForm,
    CustomSetPasswordForm
)
from .tokens import account_activation_token

# Setup logger
logger = logging.getLogger("dctfd")

# Authentication Views

class CustomLoginView(LoginView):
    """
    Custom login view with additional functionality
    """
    template_name = 'users/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        Handle valid form submission and check for first login
        """
        remember_me = self.request.POST.get('remember_me', False)
        if not remember_me:
            # Session will expire when browser is closed
            self.request.session.set_expiry(0)

        # Authentication handled by LoginView
        response = super().form_valid(form)

        # Check if user is logging in for the first time after admin creation
        user = self.request.user
        if not user.email_verified and user.is_active:
            # Redirect to change password page for first-time login
            return redirect('users:first_login')

        # Update last active timestamp
        user.update_last_active()

        # Log the successful login
        logger.info(f"User '{user.username}' logged in successfully")

        # Add a success message
        messages.success(self.request, _('You have successfully logged in.'))

        return response

    def form_invalid(self, form):
        """
        Handle invalid form submission
        """
        # Log the failed login attempt
        username = self.request.POST.get("username", "")
        ip_address = self.request.META.get("REMOTE_ADDR", "Unknown")
        logger.warning(
            f"Failed login attempt for user '{username}' from IP {ip_address}"
        )

        # Add a specific error message
        messages.error(self.request, _('Invalid username/email or password. Please try again.'))
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Determine the URL to redirect to after successful login
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('core:home')  # Changed from 'users:profile' to 'core:home'


class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = 'core:home'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            # Log the logout
            logger.info(f"User '{username}' logged out")

        # Add a message
        messages.success(request, _("You have been successfully logged out."))
        return super().dispatch(request, *args, **kwargs)


class RegisterView(View):
    """
    User registration view
    """
    template_name = 'users/register.html'
    form_class = UserRegistrationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')

        # Get the current event
        from event.models import Event

        active_event = (
            Event.objects.filter(status="registration").first()
            or Event.objects.filter(status="running").first()
        )

        if active_event:
            # Check if custom fields are enabled for this event
            try:
                event_settings = active_event.settings
                if (
                    hasattr(event_settings, "enable_user_custom_fields")
                    and event_settings.enable_user_custom_fields
                ):
                    form = self.form_class(event=active_event, field_for="user")
                    
                    # Get custom field definitions for the context
                    from django.contrib.contenttypes.models import ContentType
                    from core.custom_fields import CustomFieldDefinition
                    
                    event_content_type = ContentType.objects.get_for_model(Event)
                    custom_field_definitions = CustomFieldDefinition.objects.filter(
                        content_type=event_content_type,
                        object_id=active_event.id,
                        field_for="user"
                    ).order_by('order')
                else:
                    form = self.form_class()
                    custom_field_definitions = []
            except:
                form = self.form_class()
                custom_field_definitions = []
        else:
            form = self.form_class()
            custom_field_definitions = []

        return render(request, self.template_name, {
            'form': form,
            'custom_field_definitions': custom_field_definitions
        })

    def post(self, request):
        # Get the current event
        from event.models import Event

        active_event = (
            Event.objects.filter(status="registration").first()
            or Event.objects.filter(status="running").first()
        )

        if active_event:
            # Check if custom fields are enabled for this event
            try:
                event_settings = active_event.settings
                if (
                    hasattr(event_settings, "enable_user_custom_fields")
                    and event_settings.enable_user_custom_fields
                ):
                    form = self.form_class(
                        request.POST, event=active_event, field_for="user"
                    )
                    
                    # Get custom field definitions for the context
                    from django.contrib.contenttypes.models import ContentType
                    from core.custom_fields import CustomFieldDefinition
                    
                    event_content_type = ContentType.objects.get_for_model(Event)
                    custom_field_definitions = CustomFieldDefinition.objects.filter(
                        content_type=event_content_type,
                        object_id=active_event.id,
                        field_for="user"
                    ).order_by('order')
                else:
                    form = self.form_class(request.POST)
                    custom_field_definitions = []
            except:
                form = self.form_class(request.POST)
                custom_field_definitions = []
        else:
            form = self.form_class(request.POST)
            custom_field_definitions = []

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Set to False if email verification is required
            user.email_verified = False
            user.save()

            # Save custom fields if they exist
            if active_event and hasattr(form, "save_custom_fields"):
                form.save_custom_fields(user)

            # Send activation email if verification is enabled
            if not user.is_active:
                try:
                    from core.mailing import UserEmailService
                    UserEmailService.send_account_activation_email(
                        user=user,
                        domain=request.get_host(),
                        protocol='https' if request.is_secure() else 'http'
                    )
                    messages.success(request, 'Your account has been created. Please check your email to verify your account.')
                except Exception as e:
                    # Log the error but don't prevent the account creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send activation email: {str(e)}")
                    messages.warning(request, 'Your account has been created, but we could not send the activation email. Please contact support.')
            else:
                # Send welcome email for direct activation
                try:
                    from core.mailing import UserEmailService
                    UserEmailService.send_welcome_email(user)
                except Exception as e:
                    # Log the error but don't prevent the account creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to send welcome email: {str(e)}")

                messages.success(request, 'Your account has been created. You can now log in.')

            # Notify admins about new registration
            try:
                from core.mailing import AdminEmailService
                AdminEmailService.send_new_registration_notification(user)
            except Exception as e:
                # Log the error but don't interrupt the flow
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send admin notification: {str(e)}")

            return redirect('users:login')

        # If form is invalid, render it with errors and custom fields
        return render(request, self.template_name, {
            'form': form,
            'custom_field_definitions': custom_field_definitions
        })

    def send_activation_email(self, request, user):
        """
        Send account activation email to the user
        """
        mail_subject = 'Activate your DCTFd account'
        message = render_to_string('users/activation_email.html', {
            'user': user,
            'domain': request.get_host(),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http'
        })

        email = EmailMessage(mail_subject, message, to=[user.email])
        email.content_subtype = 'html'
        email.send()


class ActivateAccountView(View):
    """
    View for activating user account via email link
    """
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = BaseUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, BaseUser.DoesNotExist):
            user = None
            
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()
            
            # Send welcome email after successful verification
            try:
                from core.mailing import UserEmailService
                UserEmailService.send_welcome_email(user)
            except Exception as e:
                # Log the error but don't prevent activation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send welcome email: {str(e)}")
            
            messages.success(request, 'Your account has been activated. You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Activation link is invalid or has expired.')
            return redirect('users:login')


# Password Management Views

class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset request view
    """
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = PasswordResetRequestForm
    
    def form_valid(self, form):
        """
        Override to use our custom email service
        """
        # Get the email
        email = form.cleaned_data["email"]
        
        # Find active users with this email
        active_users = BaseUser.objects.filter(
            email__iexact=email, is_active=True
        )
        
        for user in active_users:
            # Use our custom email service instead of Django's default
            try:
                from core.mailing import UserEmailService
                UserEmailService.send_password_reset_email(
                    user=user,
                    domain=self.request.get_host(),
                    protocol='https' if self.request.is_secure() else 'http'
                )
            except Exception as e:
                # Log the error but don't prevent the form submission
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password reset email: {str(e)}")
            
        # Return the standard response
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Custom password reset confirmation view
    """
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    form_class = CustomSetPasswordForm
    
    def form_valid(self, form):
        """
        Override to send a confirmation email after password reset
        """
        response = super().form_valid(form)
        
        # Send confirmation email
        try:
            from core.mailing import UserEmailService
            UserEmailService.send_password_changed_email(self.user)
        except Exception as e:
            # Log the error but don't prevent the password reset
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send password changed email: {str(e)}")
        
        return response


class FirstLoginPasswordChangeView(LoginRequiredMixin, View):
    """
    View for changing password on first login (admin-created accounts)
    """
    template_name = 'users/first_login.html'
    form_class = CustomSetPasswordForm
    login_url = 'users:login'
    
    def get(self, request):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            user.email_verified = True
            user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            # Send password set confirmation email
            try:
                from core.mailing import UserEmailService
                UserEmailService.send_password_changed_email(user)
            except Exception as e:
                # Log the error but don't prevent the password change
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password changed email: {str(e)}")
            
            messages.success(request, 'Your password has been set. You can now use your account.')
            return redirect('users:profile')
            
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(View):
    """
    View for changing user password
    """
    template_name = 'users/password_change.html'
    
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            # Send password change confirmation email
            try:
                from core.mailing import UserEmailService
                UserEmailService.send_password_changed_email(user)
            except Exception as e:
                # Log the error but don't prevent the password change
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send password changed email: {str(e)}")
            
            messages.success(request, 'Your password has been updated.')
            return redirect('users:profile')
            
        return render(request, self.template_name, {'form': form})


# Profile Views

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """
    View for displaying user profile
    """
    template_name = 'users/profile.html'
    
    def get(self, request):
        context = {
            'user': request.user,
            'social_links': request.user.get_social_links(),
            'team': request.user.team,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    """
    View for editing user profile
    """
    template_name = 'users/profile_edit.html'
    form_class = ProfileUpdateForm

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        import time

        print("=" * 80)
        print(f"[DEBUG] PROFILE EDIT POST REQUEST RECEIVED - {time.time()}")
        print(f"[DEBUG] POST Data: {request.POST}")
        print(f"[DEBUG] FILES Data: {request.FILES}")

        old_avatar_id = request.user.avatar.id if request.user.avatar else None
        print(f"[DEBUG] Old Avatar ID: {old_avatar_id}")
        print(f"[DEBUG] Current User Avatar URL: {request.user.get_avatar_url()}")

        # Create form instance but don't validate yet
        form = self.form_class(request.POST, request.FILES, instance=request.user)

        # Track if any avatar changes were made
        avatar_updated = False

        # Handle custom avatar file upload first (highest priority)
        if "custom_avatar" in request.FILES:
            custom_avatar = request.FILES["custom_avatar"]
            print(f"[DEBUG] Custom avatar file detected: {custom_avatar.name}")

            # Clear any previous avatar selection when uploading custom avatar
            request.user.avatar = None
            request.user.custom_avatar = custom_avatar
            request.user.save(update_fields=["avatar", "custom_avatar"])

            print(f"[DEBUG] Custom avatar file saved and set as primary avatar")
            messages.success(
                request,
                "Custom avatar has been uploaded and set as your profile picture.",
            )
            avatar_updated = True

        # Then handle predefined avatar selection (if no custom avatar was uploaded)
        elif "avatar" in request.POST and request.POST.get("avatar"):
            selected_avatar_id = request.POST.get("avatar")
            print(f"[DEBUG] Selected Avatar ID from POST: {selected_avatar_id}")

            from users.avatar_models import AvatarOption

            try:
                avatar = AvatarOption.objects.get(id=selected_avatar_id)
                print(f"[DEBUG] Found avatar object: {avatar.id} - {avatar.name}")

                # Update avatar directly in the database
                request.user.avatar = avatar
                # Clear any custom avatar when selecting a predefined one
                request.user.custom_avatar = None
                request.user.save(update_fields=["avatar", "custom_avatar"])

                print(f"[DEBUG] Avatar updated directly: {avatar.id} - {avatar.name}")
                messages.success(
                    request, f'Avatar has been updated to "{avatar.name}".'
                )
                avatar_updated = True
            except AvatarOption.DoesNotExist:
                print(f"[DEBUG] ERROR: Avatar with ID {selected_avatar_id} not found!")
                messages.error(request, "Selected avatar not found.")

        # Force reload user to get updated avatar
        if avatar_updated:
            request.user.refresh_from_db()
            print(
                f"[DEBUG] After avatar update. Avatar URL: {request.user.get_avatar_url()}"
            )

            # Update the instance used by the form
            form = self.form_class(request.POST, request.FILES, instance=request.user)

        # Now validate the form for other fields
        print(f"[DEBUG] Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"[DEBUG] Form errors: {form.errors}")
            # Even with errors, we already updated avatar if needed
            return render(request, self.template_name, {"form": form})

        # For valid forms, save other fields too
        user = form.save(commit=False)

        # Ensure we don't overwrite the avatar changes we already made
        if avatar_updated:
            # Don't let form save override our avatar changes
            if "custom_avatar" in request.FILES:
                # Ensure custom_avatar is preserved from earlier update
                pass
            elif "avatar" in request.POST and request.POST.get("avatar"):
                # Ensure avatar is preserved from earlier update
                from users.avatar_models import AvatarOption

                try:
                    avatar = AvatarOption.objects.get(id=request.POST.get("avatar"))
                    user.avatar = avatar
                except:
                    pass

        # Save the user with any other field changes
        user.save()

        # Refresh to confirm final state
        user.refresh_from_db()
        print(
            f"[DEBUG] Final state - Avatar ID: {user.avatar.id if user.avatar else None}"
        )
        print(f"[DEBUG] Final state - Custom Avatar: {user.custom_avatar}")
        print(f"[DEBUG] Final Avatar URL: {user.get_avatar_url()}")

        # Log updated user avatar information
        logger.info(
            f"Profile update - User: {user.id} - Avatar ID: {user.avatar.id if user.avatar else 'None'}"
        )

        # Send notification about profile update
        try:
            from core.mailing import AdminEmailService

            AdminEmailService.send_profile_update_notification(user)
        except Exception as e:
            # Log the error but don't prevent the profile update
            logger.error(f"Failed to send profile update email: {str(e)}")
            print(f"[DEBUG] Failed to send profile update email: {str(e)}")

        messages.success(request, "Your profile has been updated.")
        print(f"[DEBUG] Redirecting to profile page")
        print("=" * 80)
        return redirect("users:profile")

        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class PublicProfileView(View):
    """
    View for displaying public user profile
    """
    template_name = 'users/public_profile.html'
    
    def get(self, request, username):
        user = get_object_or_404(BaseUser, username=username, is_active=True, banned=False, hidden=False)
        
        context = {
            'profile_user': user,
            'social_links': user.get_social_links(),
            'team': user.team,
        }
        return render(request, self.template_name, context)


# API Views

class UserAPI(APIView):
    """
    API endpoint for user data
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current user data
        """
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.get_full_name(),
            'score': user.score,
            'country': user.country,
            'team': user.get_team_name(),
            'is_team_captain': user.is_team_captain,
            'avatar': request.build_absolute_uri(user.get_avatar_url()),
        }
        return Response(data)


class TeamMemberSearchAPI(APIView):
    """
    API endpoint for searching users for team invitations
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Search for users to invite to team
        """
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 3:
            return Response({'error': 'Query must be at least 3 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get users who match query and don't have a team
        users = BaseUser.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query),
            team__isnull=True,
            is_active=True,
            banned=False,
            type='user'  # Only regular users can be invited to teams
        ).exclude(id=request.user.id)
        
        # Limit results
        users = users[:10]
        
        data = [{
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'avatar': request.build_absolute_uri(user.get_avatar_url()),
        } for user in users]
        
        return Response(data)

# New auth functions from CTFd

def confirm_email(request, data=None):
    """
    Confirm a user's email address using the confirmation token.
    Similar to CTFd's confirm route.
    """
    from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
    
    if not settings.EMAIL_VERIFICATION_REQUIRED:
        # If email verification is not required, redirect to challenges
        return redirect('core:challenges')
    
    # User is confirming email account
    if data and request.method == 'GET':
        signer = TimestampSigner()
        try:
            # Verify the signature and extract the email
            user_email = signer.unsign(data, max_age=1800)  # 30 minutes
            
            # Find the user with this email
            user = BaseUser.objects.get(email=user_email)
            
            # Mark the email as verified
            user.email_verified = True
            user.save()
            
            messages.success(request, 'Your email has been confirmed! You can now log in.')
            return redirect('users:login')
            
        except SignatureExpired:
            return render(request, 'users/confirm_email.html', {'errors': ['Your confirmation link has expired']})
        except (BadSignature, TypeError, BaseUser.DoesNotExist):
            return render(request, 'users/confirm_email.html', {'errors': ['Your confirmation token is invalid']})
    
    # User is trying to resend confirmation email
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'users/confirm_email.html', {'errors': ['Please provide an email address']})
        
        try:
            user = BaseUser.objects.get(email=email)
            
            if user.email_verified:
                return render(request, 'users/confirm_email.html', {'errors': ['Your email is already confirmed']})
            
            # Generate a new confirmation token
            signer = TimestampSigner()
            token = signer.sign(user.email)
            
            # Build the confirmation URL
            confirm_url = request.build_absolute_uri(reverse('users:confirm_email', args=[token]))
            
            # Send confirmation email
            subject = 'Confirm your email address'
            message = render_to_string('users/email/confirm_email.html', {
                'user': user,
                'confirm_url': confirm_url,
                'site_name': settings.SITE_NAME,
            })
            
            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            
            messages.success(request, 'A confirmation email has been sent to your address!')
            
        except BaseUser.DoesNotExist:
            # Don't reveal that the user doesn't exist for security reasons
            messages.success(request, 'A confirmation email has been sent to your address if it exists in our system!')
        
        return redirect('users:login')
    
    return render(request, 'users/confirm_email.html')

def resend_confirmation(request):
    """
    Resend confirmation email to the user.
    """
    if not settings.EMAIL_VERIFICATION_REQUIRED:
        return redirect('core:challenges')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return render(request, 'users/resend_confirmation.html', {'errors': ['Please provide an email address']})
        
        try:
            user = BaseUser.objects.get(email=email)
            
            if user.email_verified:
                return render(request, 'users/resend_confirmation.html', {'errors': ['Your email is already confirmed']})
            
            # Generate a new confirmation token
            from django.core.signing import TimestampSigner
            signer = TimestampSigner()
            token = signer.sign(user.email)
            
            # Build the confirmation URL
            confirm_url = request.build_absolute_uri(reverse('users:confirm_email', args=[token]))
            
            # Send confirmation email
            subject = 'Confirm your email address'
            message = render_to_string('users/email/confirm_email.html', {
                'user': user,
                'confirm_url': confirm_url,
                'site_name': settings.SITE_NAME,
            })
            
            email = EmailMessage(subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            
            messages.success(request, 'A confirmation email has been sent to your address!')
            
        except BaseUser.DoesNotExist:
            # Don't reveal that the user doesn't exist for security reasons
            messages.success(request, 'A confirmation email has been sent to your address if it exists in our system!')
        
        return redirect('users:login')
    
    return render(request, 'users/resend_confirmation.html')

def verify_account(request):
    """
    Verify user account with additional verification steps.
    """
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    if request.method == 'POST':
        # Implement additional verification steps here
        # This could include phone verification, identity verification, etc.
        # For now, just mark the account as verified
        
        user = request.user
        user.is_verified = True
        user.save()
        
        messages.success(request, 'Your account has been verified!')
        return redirect('core:challenges')
    
    return render(request, 'users/verify_account.html')

def oauth_login(request):
    """
    Handle OAuth login requests.
    """
    # This would integrate with OAuth providers
    # For now, just render a not implemented message
    messages.info(request, 'OAuth login is not implemented yet.')
    return redirect('users:login')

def oauth_callback(request):
    """
    Handle OAuth callback.
    """
    # This would handle OAuth callbacks
    # For now, just render a not implemented message
    messages.info(request, 'OAuth callback is not implemented yet.')
    return redirect('users:login')

@login_required
def settings(request):
    """
    User settings page.
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'two_factor_enabled': hasattr(request.user, 'two_factor') and request.user.two_factor.enabled,
    }
    
    return render(request, 'users/settings.html', context)

@login_required
def two_factor_setup(request):
    """
    Set up two-factor authentication.
    """
    # This would implement 2FA setup
    # For now, just render a not implemented message
    messages.info(request, 'Two-factor authentication is not implemented yet.')
    return redirect('users:settings')

@login_required
def two_factor_verify(request):
    """
    Verify two-factor authentication code.
    """
    # This would verify 2FA codes
    # For now, just render a not implemented message
    messages.info(request, 'Two-factor authentication verification is not implemented yet.')
    return redirect('users:settings')

@login_required
def two_factor_toggle(request):
    """
    Toggle two-factor authentication on/off.
    """
    # This would toggle 2FA on/off
    # For now, just render a not implemented message
    messages.info(request, 'Two-factor authentication toggling is not implemented yet.')
    return redirect('users:settings')


@login_required
def two_factor_disable(request):
    """
    Disable two-factor authentication.
    """
    # This would disable 2FA
    # For now, just render a not implemented message
    messages.info(
        request, "Two-factor authentication disabling is not implemented yet."
    )
    return redirect("users:settings")
