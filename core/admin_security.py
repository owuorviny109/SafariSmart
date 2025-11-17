"""
Module: core/admin_security.py
Purpose: Django admin configuration for security models

This module provides admin interfaces for managing security settings
and monitoring security events.

Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models_security import SecuritySettings, SecurityEvent


@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for Security Settings.
    
    Singleton model - only one instance exists.
    All security settings can be managed here.
    """
    
    def has_add_permission(self, request):
        """Prevent adding more than one instance."""
        return not SecuritySettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of security settings."""
        return False
    
    fieldsets = (
        ('Brute Force Protection', {
            'fields': (
                'brute_force_enabled',
                'max_login_attempts',
                'lockout_duration_minutes',
            ),
            'description': 'Protect against brute force login attacks',
        }),
        ('Rate Limiting', {
            'fields': (
                'global_rate_limit_enabled',
                'global_rate_limit_per_minute',
                'api_rate_limit_per_minute',
                'api_rate_limit_per_hour',
                'api_rate_limit_per_day',
            ),
            'description': 'Control request rates to prevent abuse',
        }),
        ('Session Security', {
            'fields': (
                'session_timeout_minutes',
                'session_expire_on_close',
                'require_https_cookies',
                'validate_session_ip',
                'validate_session_user_agent',
            ),
            'description': 'Session management and hijacking prevention',
        }),
        ('Password Security', {
            'fields': (
                'min_password_length',
                'require_uppercase',
                'require_lowercase',
                'require_numbers',
                'require_special_chars',
                'password_expiry_days',
            ),
            'description': 'Password strength requirements',
        }),
        ('Admin Security', {
            'fields': (
                'admin_ip_whitelist_enabled',
                'admin_allowed_ips',
                'admin_session_timeout_minutes',
            ),
            'description': 'Restrict and secure admin panel access',
        }),
        ('Security Headers', {
            'fields': (
                'enable_hsts',
                'hsts_max_age_seconds',
                'enable_csp',
                'enable_xss_protection',
                'enable_clickjacking_protection',
            ),
            'description': 'HTTP security headers configuration',
        }),
        ('Monitoring and Alerts', {
            'fields': (
                'enable_security_logging',
                'enable_failed_login_alerts',
                'failed_login_alert_threshold',
                'enable_suspicious_activity_alerts',
                'alert_email',
            ),
            'description': 'Security monitoring and alerting',
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['updated_at']
    
    def save_model(self, request, obj, form, change):
        """Save with username of who updated."""
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)
        
        # Log configuration change
        SecurityEvent.log_event(
            event_type='config_change',
            severity='medium',
            description=f'Security settings updated by {request.user.username}',
            user=request.user.username,
            ip_address=self.get_client_ip(request),
            details={'changes': form.changed_data}
        )
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """
    Admin interface for Security Events.
    
    View and manage security events with filtering and search.
    """
    
    list_display = [
        'timestamp',
        'event_type_display',
        'severity_display',
        'user',
        'ip_address',
        'path',
        'resolved_display',
    ]
    
    list_filter = [
        'event_type',
        'severity',
        'resolved',
        ('timestamp', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'user',
        'ip_address',
        'description',
        'path',
    ]
    
    readonly_fields = [
        'event_type',
        'severity',
        'timestamp',
        'user',
        'ip_address',
        'user_agent',
        'path',
        'description',
        'details',
    ]
    
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'event_type',
                'severity',
                'timestamp',
            ),
        }),
        ('User & Request Details', {
            'fields': (
                'user',
                'ip_address',
                'user_agent',
                'path',
            ),
        }),
        ('Description', {
            'fields': (
                'description',
                'details',
            ),
        }),
        ('Resolution', {
            'fields': (
                'resolved',
                'resolved_at',
                'resolved_by',
            ),
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def has_add_permission(self, request):
        """Events are auto-generated, not manually created."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow changing resolution status only."""
        return True
    
    def event_type_display(self, obj):
        """Display event type."""
        return obj.get_event_type_display()
    event_type_display.short_description = 'Event Type'
    
    def severity_display(self, obj):
        """Display severity with color coding."""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display().upper()
        )
    severity_display.short_description = 'Severity'
    
    def resolved_display(self, obj):
        """Display resolution status."""
        if obj.resolved:
            return format_html(
                '<span style="color: green;">Resolved</span>'
            )
        return format_html(
            '<span style="color: orange;">Pending</span>'
        )
    resolved_display.short_description = 'Status'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected events as resolved."""
        count = queryset.update(
            resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user.username
        )
        self.message_user(
            request,
            f'{count} event(s) marked as resolved.'
        )
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_unresolved(self, request, queryset):
        """Mark selected events as unresolved."""
        count = queryset.update(
            resolved=False,
            resolved_at=None,
            resolved_by=''
        )
        self.message_user(
            request,
            f'{count} event(s) marked as unresolved.'
        )
    mark_as_unresolved.short_description = 'Mark as unresolved'
