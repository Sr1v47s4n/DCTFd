"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

# This file is kept for backward compatibility but functionality is moved to custom_admin

# Import the models for reference
from .models import (
    PlatformConfiguration, SystemLog, 
    BackupConfiguration, MaintenanceWindow
)

# Helper classes for custom admin panel
class PlatformConfigurationHelper:
    """Helper class for managing platform configuration in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for platform configuration"""
        return {
            'site_fields': ['site_name', 'site_description', 'platform_logo', 'favicon', 'platform_version'],
            'contact_fields': ['admin_email', 'support_email'],
            'social_fields': ['twitter_handle', 'facebook_url', 'discord_invite', 'github_url'],
            'feature_fields': ['enable_registration', 'require_email_verification', 'enable_team_creation', 'enable_public_scoreboard'],
            'team_fields': ['max_team_size'],
            'rate_limiting_fields': ['max_login_attempts', 'max_submissions_per_minute'],
            'maintenance_fields': ['maintenance_mode', 'maintenance_message'],
            'analytics_fields': ['enable_analytics', 'analytics_code'],
            'terms_fields': ['terms_of_service', 'privacy_policy'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for platform configuration table"""
        return ['site_name', 'admin_email', 'maintenance_mode', 'last_updated']
    
    @staticmethod
    def is_singleton():
        """Returns whether this model should have only one instance"""
        return True

class SystemLogHelper:
    """Helper class for managing system logs in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for system logs"""
        return {
            'log_fields': ['timestamp', 'level', 'category', 'message'],
            'user_fields': ['user', 'ip_address', 'user_agent'],
            'additional_fields': ['additional_data'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for system logs table"""
        return ['timestamp', 'level', 'category', 'message_preview', 'user']
    
    @staticmethod
    def get_list_filters():
        """Returns the list filters for system logs"""
        return ['level', 'category', 'timestamp']
    
    @staticmethod
    def get_search_fields():
        """Returns the search fields for system logs"""
        return ['message', 'user__username', 'ip_address']
    
    @staticmethod
    def get_readonly():
        """Returns fields that should be readonly"""
        return ['timestamp', 'level', 'category', 'message', 'user', 'ip_address', 'user_agent', 'additional_data']

class BackupConfigurationHelper:
    """Helper class for managing backup configuration in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for backup configuration"""
        return {
            'basic_fields': ['name', 'enabled', 'backup_type', 'frequency'],
            'custom_schedule_fields': ['custom_cron'],
            'storage_fields': ['storage_type', 'storage_path', 'storage_credentials', 'retention_count'],
            'option_fields': ['compress', 'encrypt', 'notification_email'],
            'status_fields': ['last_backup_time', 'last_backup_status'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for backup configuration table"""
        return ['name', 'backup_type', 'frequency', 'storage_type', 'enabled', 'last_backup_time']
    
    @staticmethod
    def get_list_filters():
        """Returns the list filters for backup configuration"""
        return ['enabled', 'backup_type', 'frequency', 'storage_type']
    
    @staticmethod
    def get_search_fields():
        """Returns the search fields for backup configuration"""
        return ['name', 'storage_path']
    
    @staticmethod
    def get_readonly_fields():
        """Returns fields that should be readonly when editing"""
        return ['last_backup_time', 'last_backup_status']

class MaintenanceWindowHelper:
    """Helper class for managing maintenance windows in the custom admin panel"""
    
    @staticmethod
    def get_fields():
        """Returns the fields used in the custom admin panel for maintenance windows"""
        return {
            'basic_fields': ['title', 'description', 'start_time', 'end_time', 'status'],
            'impact_fields': ['complete_downtime', 'affects_registration', 'affects_challenges', 
                            'affects_submissions', 'affects_scoreboard'],
            'visibility_fields': ['visible_to_users', 'created_by'],
        }
    
    @staticmethod
    def get_list_display():
        """Returns the list display fields for maintenance windows table"""
        return ['title', 'start_time', 'end_time', 'status', 'complete_downtime', 'visible_to_users']
    
    @staticmethod
    def get_list_filters():
        """Returns the list filters for maintenance windows"""
        return ['status', 'complete_downtime', 'visible_to_users']
    
    @staticmethod
    def get_search_fields():
        """Returns the search fields for maintenance windows"""
        return ['title', 'description']
    
    @staticmethod
    def get_readonly_fields():
        """Returns fields that should be readonly when editing"""
        return ['created_at', 'created_by']
    
    @staticmethod
    def get_actions():
        """Returns custom actions for maintenance windows"""
        return ['activate_maintenance', 'complete_maintenance']
