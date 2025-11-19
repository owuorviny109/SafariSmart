"""
Module: core/admin_pages.py
Purpose: Admin interface for static pages

This module provides the Django admin interface for managing
static content pages.

Author: SafariSmart Kenya Team
Date: 2025-11-19
"""

from django.contrib import admin
from django.utils.html import format_html
from .models_pages import StaticPage, ContactInfo


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for ContactInfo model (Singleton).
    
    Manages contact details and social links.
    """
    
    fieldsets = (
        ('Contact Details', {
            'fields': ('email', 'phone', 'location')
        }),
        ('Social Media Links', {
            'fields': ('github_url', 'linkedin_url', 'twitter_url'),
            'description': 'Add your social media profile URLs'
        }),
        ('Portfolio', {
            'fields': ('portfolio_url', 'portfolio_text')
        }),
        ('Footer Content', {
            'fields': ('about_text', 'creator_name')
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one instance."""
        return not ContactInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """
    Admin interface for StaticPage model.
    
    Provides rich text editing, preview, and organization features
    for managing static content pages.
    """
    
    list_display = [
        'title',
        'slug',
        'is_published_badge',
        'show_in_footer_badge',
        'footer_order',
        'view_page_link',
        'updated_at'
    ]
    
    list_filter = [
        'is_published',
        'show_in_footer',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'title',
        'slug',
        'content',
        'meta_description'
    ]
    
    prepopulated_fields = {
        'slug': ('title',)
    }
    
    fieldsets = (
        ('Page Information', {
            'fields': ('title', 'slug')
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'You can use HTML for formatting. Use <h2>, <p>, <ul>, <li>, etc.'
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Visibility', {
            'fields': ('is_published', 'show_in_footer', 'footer_order')
        }),
    )
    
    readonly_fields = []
    
    def is_published_badge(self, obj):
        """Display published status as badge."""
        if obj.is_published:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-size: 12px; font-weight: 600;">Published</span>'
            )
        return format_html(
            '<span style="background: #6b7280; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 12px; font-weight: 600;">Draft</span>'
        )
    is_published_badge.short_description = 'Status'
    
    def show_in_footer_badge(self, obj):
        """Display footer visibility as badge."""
        if obj.show_in_footer:
            return format_html(
                '<span style="color: #10b981;">✓ Yes</span>'
            )
        return format_html(
            '<span style="color: #6b7280;">✗ No</span>'
        )
    show_in_footer_badge.short_description = 'In Footer'
    
    def view_page_link(self, obj):
        """Display link to view page on site."""
        if obj.is_published:
            return format_html(
                '<a href="{}" target="_blank" style="color: #2D7A4F; text-decoration: none;">'
                'View Page →</a>',
                obj.get_absolute_url()
            )
        return format_html(
            '<span style="color: #9ca3af;">Not published</span>'
        )
    view_page_link.short_description = 'View'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
