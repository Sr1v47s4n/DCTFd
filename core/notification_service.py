"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from core.models import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for managing and sending notifications to users.
    """
    
    NOTIFICATION_TYPES = {
        'system': 'System',
        'event': 'Event',
        'team': 'Team',
        'challenge': 'Challenge',
        'achievement': 'Achievement',
        'message': 'Message',
        'announcement': 'Announcement'
    }
    
    DISPLAY_TYPES = {
        'toast': 'Toast',
        'push': 'Push Notification',
        'alert': 'Alert', 
        'banner': 'Banner'
    }
    
    SOUND_OPTIONS = {
        'none': 'No Sound',
        'notification': 'Notification', 
        'success': 'Success',
        'error': 'Error'
    }
    
    @classmethod
    def send_notification(cls, 
                          user, 
                          title, 
                          message, 
                          notification_type='system', 
                          display_type='toast',
                          sound='notification',
                          link=None, 
                          event=None, 
                          team=None, 
                          challenge=None,
                          metadata=None,
                          scheduled_time=None):
        """
        Send a notification to a user.
        
        Args:
            user: User model instance or User ID
            title: Notification title
            message: Notification message
            notification_type: Type of notification (system, event, team, etc.)
            display_type: How to display the notification (toast, push, alert, banner)
            sound: Sound to play (notification, alert, success, error, etc.)
            link: Optional URL to redirect to
            event: Associated event (if any)
            team: Associated team (if any)
            challenge: Associated challenge (if any)
            metadata: Additional metadata for the notification as dict
            scheduled_time: When to display the notification (None for immediate)
            
        Returns:
            Notification instance
        """
        # Create metadata if not provided
        if metadata is None:
            metadata = {}
            
        # Add display type and sound to metadata
        metadata['display_type'] = display_type
        metadata['sound'] = sound
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type,
            link=link,
            event=event,
            team=team,
            challenge=challenge,
            metadata=metadata
        )
        
        # If scheduled, update created_at time
        if scheduled_time:
            notification.created_at = scheduled_time
            notification.save(update_fields=['created_at'])
            
        logger.info(f"Notification created: {notification.id} for user {user.id} - {title}")
        return notification
    
    @classmethod
    def send_notification_to_all(cls, 
                                title, 
                                message, 
                                notification_type='announcement',
                                display_type='alert',
                                sound='notification',
                                link=None,
                                event=None,
                                metadata=None,
                                scheduled_time=None):
        """
        Send a notification to all users.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            display_type: How to display the notification
            sound: Sound to play
            link: Optional URL to redirect to
            event: Associated event (if any)
            metadata: Additional metadata for the notification
            scheduled_time: When to display the notification
            
        Returns:
            List of created notification instances
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get all active users
        users = User.objects.filter(is_active=True)
        
        notifications = []
        for user in users:
            notification = cls.send_notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                display_type=display_type,
                sound=sound,
                link=link,
                event=event,
                metadata=metadata,
                scheduled_time=scheduled_time
            )
            notifications.append(notification)
            
        logger.info(f"Sent notification to {len(notifications)} users: {title}")
        return notifications
    
    @classmethod
    def send_notification_to_event(cls,
                                  event,
                                  title,
                                  message,
                                  notification_type='event',
                                  display_type='toast',
                                  sound='notification',
                                  link=None,
                                  metadata=None,
                                  scheduled_time=None):
        """
        Send a notification to all users registered for an event.
        
        Args:
            event: Event model instance
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            display_type: How to display the notification
            sound: Sound to play
            link: Optional URL to redirect to
            metadata: Additional metadata for the notification
            scheduled_time: When to display the notification
            
        Returns:
            List of created notification instances
        """
        # Get all users registered for this event
        from event.models import EventRegistration
        registrations = EventRegistration.objects.filter(
            event=event, 
            status='approved'
        ).select_related('user')
        
        notifications = []
        for reg in registrations:
            notification = cls.send_notification(
                user=reg.user,
                title=title,
                message=message,
                notification_type=notification_type,
                display_type=display_type,
                sound=sound,
                link=link,
                event=event,
                metadata=metadata,
                scheduled_time=scheduled_time
            )
            notifications.append(notification)
            
        logger.info(f"Sent notification to {len(notifications)} event participants: {title}")
        return notifications
    
    @classmethod
    def get_pending_notifications(cls, user, max_age_days=7):
        """
        Get all unread notifications for a user within the specified timeframe.
        
        Args:
            user: User model instance
            max_age_days: Maximum age of notifications to retrieve (in days)
            
        Returns:
            QuerySet of Notification instances
        """
        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=max_age_days)
        
        # Get all unread notifications that are not scheduled for the future
        notifications = Notification.objects.filter(
            user=user,
            is_read=False,
            created_at__gte=cutoff_date,
            created_at__lte=timezone.now()
        ).order_by('-created_at')
        
        return notifications
    
    @classmethod
    def mark_all_as_read(cls, user):
        """
        Mark all notifications as read for a user.
        
        Args:
            user: User model instance
            
        Returns:
            Number of notifications marked as read
        """
        # Get all unread notifications
        notifications = Notification.objects.filter(
            user=user,
            is_read=False
        )
        
        # Update them all at once
        count = notifications.count()
        notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        logger.info(f"Marked {count} notifications as read for user {user.id}")
        return count
    
    @classmethod
    def get_scheduled_notifications(cls):
        """
        Get all scheduled notifications that should be sent now.
        
        Returns:
            QuerySet of Notification instances
        """
        # Get all notifications scheduled for the past or now but not marked as read
        notifications = Notification.objects.filter(
            Q(metadata__has_key='scheduled') & Q(metadata__scheduled=True),
            is_read=False,
            created_at__lte=timezone.now()
        )
        
        return notifications
