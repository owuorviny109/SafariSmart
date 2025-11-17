"""
Module: core/admin_config.py
Purpose: Django admin configuration for configuration models

This module registers configuration models with Django admin and
provides user-friendly interfaces for managing application settings.

Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from django.contrib import admin
from django.utils.html import format_html
from .models_config import (
    TravelType,
    BudgetCategory,
    InterestCategory,
    BudgetEstimate,
    SystemConfiguration
)


@admin.register(TravelType)
class TravelTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for TravelType model.
    
    Provides intuitive interface for managing travel types with
    inline editing, filtering, and search capabilities.
    """
    
    list_display = [
        'name',
        'code',
        'icon_display',
        'is_active',
        'sort_order',
        'updated_at'
    ]
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'sort_order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def icon_display(self, obj):
        """Display icon in list view."""
        if obj.icon:
            return format_html('<span style="font-size: 20px;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = 'Icon'


@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for BudgetCategory model.
    
    Manages budget categories with inline budget estimates.
    """
    
    list_display = [
        'name',
        'code',
        'budget_range_display',
        'is_active',
        'sort_order',
        'updated_at'
    ]
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['sort_order', 'min_budget_per_day']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Budget Range', {
            'fields': ('min_budget_per_day', 'max_budget_per_day'),
            'description': 'Daily budget range in KSh'
        }),
        ('Display Settings', {
            'fields': ('icon', 'sort_order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def budget_range_display(self, obj):
        """Display budget range formatted."""
        return f"KSh {obj.min_budget_per_day:,} - {obj.max_budget_per_day:,}"
    budget_range_display.short_description = 'Daily Budget Range'


@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for InterestCategory model.
    
    Manages user interest categories with easy activation/deactivation.
    """
    
    list_display = [
        'name',
        'code',
        'icon_display',
        'is_active',
        'sort_order',
        'updated_at'
    ]
    list_editable = ['is_active', 'sort_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon', 'sort_order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def icon_display(self, obj):
        """Display icon in list view."""
        if obj.icon:
            return format_html('<span style="font-size: 20px;">{}</span>', obj.icon)
        return '-'
    icon_display.short_description = 'Icon'


@admin.register(BudgetEstimate)
class BudgetEstimateAdmin(admin.ModelAdmin):
    """
    Admin interface for BudgetEstimate model.
    
    Manages daily cost estimates for each budget category.
    """
    
    list_display = [
        'budget_category',
        'accommodation_range',
        'activities_range',
        'meals_range',
        'transport_range',
        'total_range',
        'updated_at'
    ]
    list_filter = ['budget_category', 'updated_at']
    search_fields = ['budget_category__name', 'notes']
    
    fieldsets = (
        ('Budget Category', {
            'fields': ('budget_category',)
        }),
        ('Accommodation Costs', {
            'fields': ('accommodation_min', 'accommodation_max'),
            'description': 'Daily accommodation costs in KSh'
        }),
        ('Activities Costs', {
            'fields': ('activities_min', 'activities_max'),
            'description': 'Daily activities costs in KSh'
        }),
        ('Meals Costs', {
            'fields': ('meals_min', 'meals_max'),
            'description': 'Daily meals costs in KSh'
        }),
        ('Transport Costs', {
            'fields': ('transport_min', 'transport_max'),
            'description': 'Daily transport costs in KSh'
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def accommodation_range(self, obj):
        """Display accommodation range."""
        return f"KSh {obj.accommodation_min:,} - {obj.accommodation_max:,}"
    accommodation_range.short_description = 'Accommodation'
    
    def activities_range(self, obj):
        """Display activities range."""
        return f"KSh {obj.activities_min:,} - {obj.activities_max:,}"
    activities_range.short_description = 'Activities'
    
    def meals_range(self, obj):
        """Display meals range."""
        return f"KSh {obj.meals_min:,} - {obj.meals_max:,}"
    meals_range.short_description = 'Meals'
    
    def transport_range(self, obj):
        """Display transport range."""
        return f"KSh {obj.transport_min:,} - {obj.transport_max:,}"
    transport_range.short_description = 'Transport'
    
    def total_range(self, obj):
        """Display total daily cost range."""
        total_min = obj.get_total_min()
        total_max = obj.get_total_max()
        return format_html(
            '<strong>KSh {} - {}</strong>',
            f'{total_min:,}',
            f'{total_max:,}'
        )
    total_range.short_description = 'Total Daily'


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for SystemConfiguration model.
    
    Singleton model for global system settings. Only one instance exists.
    """
    
    def has_add_permission(self, request):
        """Prevent adding more than one configuration."""
        return not SystemConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of configuration."""
        return False
    
    fieldsets = (
        (' System Control', {
            'fields': ('maintenance_mode', 'maintenance_message'),
            'description': 'Control system availability',
            'classes': ('wide',)
        }),
        (' Feature Flags', {
            'fields': (
                'enable_ai_generation',
                'enable_weather_forecasts',
                'enable_custom_destinations',
                'enable_user_registration',
                'enable_itinerary_sharing',
                'enable_itinerary_saving',
            ),
            'description': 'Enable or disable features with one click'
        }),
        (' Rate Limiting', {
            'fields': (
                'enable_rate_limiting',
                'max_itineraries_per_day',
                'max_itineraries_per_hour',
            ),
            'description': 'Control usage limits to prevent abuse'
        }),
        (' Analytics & Tracking', {
            'fields': (
                'enable_analytics',
                'google_analytics_id',
                'enable_error_reporting',
            ),
            'description': 'Analytics and error tracking settings'
        }),
        (' Announcement Banner', {
            'fields': (
                'show_announcement',
                'announcement_text',
                'announcement_type',
                'announcement_link',
                'announcement_link_text',
            ),
            'description': 'Display announcements to users',
            'classes': ('collapse',)
        }),
        (' Trip Constraints', {
            'fields': (
                'min_trip_duration',
                'max_trip_duration',
                'min_budget',
                'max_budget',
            ),
            'description': 'Trip duration and budget limits',
            'classes': ('collapse',)
        }),
        (' Traveler Constraints', {
            'fields': (
                'min_adults',
                'max_adults',
                'max_children',
                'max_total_travelers',
                'max_destinations',
                'max_interests',
            ),
            'description': 'Traveler and selection limits',
            'classes': ('collapse',)
        }),
        (' SEO Settings', {
            'fields': (
                'site_name',
                'site_tagline',
                'meta_description',
            ),
            'description': 'Search engine optimization settings',
            'classes': ('collapse',)
        }),
        (' Contact & Social', {
            'fields': (
                'support_email',
                'support_phone',
                'facebook_url',
                'twitter_url',
                'instagram_url',
                'youtube_url',
            ),
            'description': 'Contact information and social media links',
            'classes': ('collapse',)
        }),
        (' Email Settings', {
            'fields': (
                'enable_email_notifications',
                'admin_notification_email',
            ),
            'description': 'Email notification settings',
            'classes': ('collapse',)
        }),
        (' API Settings', {
            'fields': (
                'gemini_api_rate_limit',
                'weather_api_cache_hours',
            ),
            'description': 'External API configuration',
            'classes': ('collapse',)
        }),
        ('ℹ️ Version Information', {
            'fields': (
                'app_version',
                'last_deployment_date',
            ),
            'description': 'Application version tracking',
            'classes': ('collapse',)
        }),
        ('📝 Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['updated_at']
    
    def save_model(self, request, obj, form, change):
        """Save with username of who updated."""
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)



# API Usage Tracking Admin

from .models_api_tracking import APIUsageLog, APIUsageStats


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """
    Admin interface for API usage logs.
    
    Provides real-time view of all API calls with filtering and search.
    """
    
    list_display = [
        'request_time',
        'api_name',
        'status_display',
        'response_time_display',
        'tokens_used',
        'cost_display',
    ]
    list_filter = [
        'api_name',
        'status',
        ('request_time', admin.DateFieldListFilter),
    ]
    search_fields = ['error_message', 'ip_address']
    readonly_fields = [
        'api_name',
        'endpoint',
        'request_time',
        'response_time',
        'status',
        'tokens_used',
        'estimated_cost',
        'error_message',
        'user_id',
        'ip_address',
        'request_data',
        'response_data',
    ]
    date_hierarchy = 'request_time'
    
    def has_add_permission(self, request):
        """Prevent manual creation of logs."""
        return False
        
    def has_change_permission(self, request, obj=None):
        """Logs are read-only."""
        return False
        
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'success': 'green',
            'failure': 'red',
            'rate_limited': 'orange',
            'queued': 'blue',
            'timeout': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def response_time_display(self, obj):
        """Display response time formatted."""
        if obj.response_time is None:
            return '-'
        return f"{obj.response_time:.2f}s"
    response_time_display.short_description = 'Response Time'
    
    def cost_display(self, obj):
        """Display cost in both USD and KSh."""
        return format_html(
            '${} <span style="color: gray;">(KSh {})</span>',
            f'{obj.estimated_cost:.4f}',
            f'{obj.cost_in_ksh:.2f}'
        )
    cost_display.short_description = 'Cost'


@admin.register(APIUsageStats)
class APIUsageStatsAdmin(admin.ModelAdmin):
    """
    Admin interface for API usage statistics.
    
    Shows aggregated statistics by hour/day/month.
    """
    
    list_display = [
        'period_start',
        'api_name',
        'period_type',
        'total_calls',
        'success_rate_display',
        'total_cost_display',
        'avg_response_time_display',
    ]
    list_filter = [
        'api_name',
        'period_type',
        ('period_start', admin.DateFieldListFilter),
    ]
    readonly_fields = [
        'api_name',
        'period_type',
        'period_start',
        'total_calls',
        'successful_calls',
        'failed_calls',
        'rate_limited_calls',
        'queued_calls',
        'total_tokens',
        'total_cost',
        'avg_response_time',
        'updated_at',
    ]
    date_hierarchy = 'period_start'
    
    def has_add_permission(self, request):
        """Stats are auto-generated."""
        return False
        
    def has_change_permission(self, request, obj=None):
        """Stats are read-only."""
        return False
        
    def success_rate_display(self, obj):
        """Display success rate with color."""
        rate = obj.success_rate
        color = 'green' if rate >= 95 else 'orange' if rate >= 80 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            f'{rate:.1f}'
        )
    success_rate_display.short_description = 'Success Rate'
    
    def total_cost_display(self, obj):
        """Display total cost in USD and KSh."""
        return format_html(
            '${} <span style="color: gray;">(KSh {})</span>',
            f'{obj.total_cost:.2f}',
            f'{obj.cost_in_ksh:.2f}'
        )
    total_cost_display.short_description = 'Total Cost'
    
    def avg_response_time_display(self, obj):
        """Display average response time."""
        if obj.avg_response_time is None:
            return '-'
        return f"{obj.avg_response_time:.2f}s"
    avg_response_time_display.short_description = 'Avg Response'
