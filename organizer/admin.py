"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

# This file is kept for backward compatibility but functionality is moved to custom_admin

# Import the models for reference
from .models import Event, EventAnnouncement, EventSettings, EventRegistration, OrganizerTaskAssignment

# Custom forms and widgets can be defined here and imported in custom_admin views

class EventAdminHelper:
    """Helper class for managing events in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for events"""
        return {
            'basic_fields': ['name', 'description', 'short_description', 'logo', 'banner'],
            'timing_fields': ['start_time', 'end_time', 'registration_start', 'registration_end'],
            'status_fields': ['status', 'public', 'registration_open'],
            'team_fields': ['max_team_size', 'min_team_size', 'allow_individual_participants'],
            'organization_fields': ['organizers'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for events table"""
        return ['name', 'status', 'start_time', 'end_time', 'public', 'registration_open']
    
    @staticmethod
    def get_list_filters():
        """Returns the list filters for events"""
        return ['status', 'public', 'registration_open']

class EventAnnouncementAdminHelper:
    """Helper class for managing event announcements in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for event announcements"""
        return {
            'basic_fields': ['title', 'content', 'event', 'author'],
            'publishing_fields': ['important', 'publish_time'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for announcements table"""
        return ['title', 'event', 'author', 'important', 'publish_time']
    
    @staticmethod
    def get_list_filters():
        """Returns the list filters for announcements"""
        return ['event', 'important', 'publish_time']

# Similar helper classes for other models
class EventSettingsAdminHelper:
    @staticmethod
    def get_fields():
        return {
            'event_field': ['event'],
            'scoring_fields': ['use_dynamic_scoring', 'show_scoreboard', 'freeze_scoreboard_at', 'show_challenge_details'],
            'registration_fields': ['require_email_verification', 'allow_team_changes', 'team_change_cutoff'],
            'feature_fields': ['enable_hints', 'enable_team_chat', 'enable_challenge_feedback', 'theme'],
        }
    
    @staticmethod
    def get_list_display():
        return ['event', 'show_scoreboard', 'use_dynamic_scoring', 'enable_hints']

class EventRegistrationAdminHelper:
    @staticmethod
    def get_fields():
        return {
            'registration_fields': ['user', 'team', 'event', 'status', 'registered_at'],
            'additional_fields': ['notes', 'eligibility_confirmed'],
            'organizer_fields': ['organizer_notes'],
        }
    
    @staticmethod
    def get_list_display():
        return ['user', 'team_name', 'event', 'status', 'registered_at']
    
    @staticmethod
    def get_actions():
        return ['approve_registrations', 'reject_registrations', 'waitlist_registrations']

class OrganizerTaskAssignmentAdminHelper:
    @staticmethod
    def get_fields():
        return {
            'task_fields': ['title', 'description', 'event'],
            'assignment_fields': ['assigned_to', 'assigned_by', 'status', 'priority'],
            'timing_fields': ['due_date', 'created_at', 'completed_at'],
        }
    
    @staticmethod
    def get_list_display():
        return ['title', 'event', 'assigned_to', 'status', 'priority', 'due_date']
    
    @staticmethod
    def get_actions():
        return ['mark_completed']
