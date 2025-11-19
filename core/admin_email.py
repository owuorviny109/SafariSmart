"""
Email Management Admin Interface

This module provides Django admin interfaces for managing email templates
and viewing email logs.

Author: SafariSmart Kenya Team
Date: 2025-11-19
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from .models_email import EmailTemplate, EmailLog, EmailSettings


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for Email Templates.
    
    Allows admins to create and edit email templates with preview functionality.
    """
    
    list_display = [
        'name', 
        'email_type', 
        'subject_preview', 
        'is_active', 
        'emails_sent_count',
        'updated_at'
    ]
    
    list_filter = [
        'email_type', 
        'is_active', 
        'created_at', 
        'updated_at'
    ]
    
    search_fields = [
        'name', 
        'subject', 
        'html_content'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'emails_sent_count',
        'preview_html'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Template Help', {
            'fields': ('available_variables',),
            'classes': ('collapse',)
        }),
        ('Preview & Stats', {
            'fields': ('preview_html', 'emails_sent_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_preview(self, obj):
        """Show truncated subject in list view"""
        if len(obj.subject) > 50:
            return obj.subject[:50] + '...'
        return obj.subject
    subject_preview.short_description = 'Subject'
    
    def emails_sent_count(self, obj):
        """Count of emails sent using this template"""
        count = obj.logs.filter(status='sent').count()
        if count > 0:
            url = reverse('admin:core_emaillog_changelist')
            return format_html(
                '<a href="{}?template__id__exact={}">{} sent</a>',
                url, obj.id, count
            )
        return '0 sent'
    emails_sent_count.short_description = 'Emails Sent'
    
    def preview_html(self, obj):
        """Show HTML preview of the template"""
        if obj.html_content:
            # Sample context for preview
            sample_context = {
                'user': {
                    'first_name': 'John',
                    'username': 'john_doe',
                    'email': 'john@example.com'
                },
                'site_name': 'SafariSmart Kenya',
                'login_url': '/accounts/login/',
            }
            
            try:
                preview = obj.render_html_content(sample_context)
                return format_html(
                    '<div style="border: 1px solid #ddd; padding: 10px; max-height: 300px; overflow-y: auto;">{}</div>',
                    mark_safe(preview)
                )
            except Exception as e:
                return format_html(
                    '<div style="color: red;">Preview Error: {}</div>',
                    str(e)
                )
        return 'No HTML content'
    preview_html.short_description = 'HTML Preview'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        return super().get_queryset(request).prefetch_related('logs')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Email Logs.
    
    Provides read-only view of all emails sent through the system.
    """
    
    list_display = [
        'subject_preview',
        'recipient_email',
        'template_name',
        'status_badge',
        'created_at',
        'sent_at'
    ]
    
    list_filter = [
        'status',
        'template__email_type',
        'created_at',
        'sent_at'
    ]
    
    search_fields = [
        'subject',
        'recipient_email',
        'template__name'
    ]
    
    readonly_fields = [
        'template',
        'recipient_email',
        'subject',
        'status',
        'error_message',
        'created_at',
        'sent_at'
    ]
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Disable adding email logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make email logs read-only"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return request.user.is_superuser
    
    def subject_preview(self, obj):
        """Show truncated subject"""
        if len(obj.subject) > 60:
            return obj.subject[:60] + '...'
        return obj.subject
    subject_preview.short_description = 'Subject'
    
    def template_name(self, obj):
        """Show template name with link"""
        if obj.template:
            url = reverse('admin:core_emailtemplate_change', args=[obj.template.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.template.name
            )
        return 'N/A'
    template_name.short_description = 'Template'
    
    def status_badge(self, obj):
        """Show status with color coding"""
        colors = {
            'sent': 'green',
            'sending': 'orange',
            'failed': 'red',
            'bounced': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('template')


# Custom admin actions
def resend_failed_emails(modeladmin, request, queryset):
    """Admin action to resend failed emails"""
    failed_logs = queryset.filter(status='failed')
    resent_count = 0
    
    for log in failed_logs:
        if log.template and log.template.is_active:
            # Try to resend
            context = {'user': {'email': log.recipient_email}}  # Basic context
            if log.template.send_email(log.recipient_email, context):
                resent_count += 1
    
    modeladmin.message_user(
        request,
        f'Successfully resent {resent_count} emails.'
    )

resend_failed_emails.short_description = "Resend selected failed emails"

# Add the action to EmailLogAdmin
EmailLogAdmin.actions = [resend_failed_emails]


@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for Email Settings.
    
    Allows business to configure email addresses and settings.
    """
    
    fieldsets = (
        ('Email Addresses', {
            'fields': (
                'default_from_email',
                'support_email', 
                'booking_email',
                'marketing_email'
            ),
            'description': 'Configure the email addresses used for different types of emails.'
        }),
        ('Company Branding', {
            'fields': (
                'company_name',
                'company_tagline'
            ),
            'description': 'Company information displayed in emails.'
        }),
        ('Email Features', {
            'fields': (
                'enable_email_notifications',
                'enable_welcome_emails',
                'enable_trip_notifications', 
                'enable_marketing_emails'
            ),
            'description': 'Control which types of emails are sent.'
        }),
        ('SMTP Settings (Optional)', {
            'fields': (
                'smtp_host',
                'smtp_port',
                'smtp_username',
                'smtp_use_tls'
            ),
            'classes': ('collapse',),
            'description': 'Override default SMTP settings from .env file (leave blank to use .env settings).'
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        """Only allow one EmailSettings instance"""
        return not EmailSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of EmailSettings"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Redirect to change view if settings exist, otherwise show add form"""
        if EmailSettings.objects.exists():
            settings = EmailSettings.objects.first()
            return redirect(f'/admin/core/emailsettings/{settings.pk}/change/')
        return super().changelist_view(request, extra_context)
    
    def response_add(self, request, obj, post_url_override=None):
        """After adding, redirect to change view"""
        return redirect(f'/admin/core/emailsettings/{obj.pk}/change/')
    
    def response_change(self, request, obj):
        """After changing, stay on the same page"""
        return redirect(f'/admin/core/emailsettings/{obj.pk}/change/')
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add email statistics to the change view"""
        extra_context = extra_context or {}
        
        # Get email statistics
        from datetime import datetime, timedelta
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        total_emails = EmailLog.objects.count()
        emails_this_week = EmailLog.objects.filter(created_at__date__gte=week_ago).count()
        failed_emails = EmailLog.objects.filter(status='failed').count()
        
        extra_context.update({
            'total_emails_sent': total_emails,
            'emails_this_week': emails_this_week,
            'failed_emails': failed_emails,
        })
        
        return super().change_view(request, object_id, form_url, extra_context)