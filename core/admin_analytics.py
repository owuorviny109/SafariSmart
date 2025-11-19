"""
Analytics Admin Interface

Privacy-compliant analytics dashboard for SafariSmart Kenya.
Shows visitor traffic, popular pages, and business metrics.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models_privacy_analytics import (
    ConsentRecord, 
    AnonymousPageView, 
    BusinessMetrics
)


@admin.register(AnonymousPageView)
class AnonymousPageViewAdmin(admin.ModelAdmin):
    """
    View anonymous page views - see your website traffic!
    """
    
    list_display = [
        'path',
        'page_category', 
        'device_type',
        'browser_family',
        'country_display',
        'timestamp'
    ]
    
    list_filter = [
        'page_category',
        'is_mobile',
        'browser_family',
        'country_code',
        'timestamp'
    ]
    
    search_fields = ['path']
    
    date_hierarchy = 'timestamp'
    
    readonly_fields = [
        'anonymous_id',
        'path',
        'page_category',
        'is_mobile',
        'browser_family',
        'country_code',
        'timestamp'
    ]
    
    def has_add_permission(self, request):
        """Don't allow manual addition"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make read-only"""
        return False
    
    def device_type(self, obj):
        """Show device type with icon"""
        if obj.is_mobile:
            return format_html('<i class="bi bi-phone" style="color: #28a745;"></i> Mobile')
        return format_html('<i class="bi bi-laptop" style="color: #007bff;"></i> Desktop')
    device_type.short_description = 'Device'
    
    def country_display(self, obj):
        """Show country with flag emoji"""
        if obj.country_code:
            # Simple country code to flag mapping
            flag_map = {
                'KE': '🇰🇪', 'US': '🇺🇸', 'GB': '🇬🇧', 'CA': '🇨🇦',
                'AU': '🇦🇺', 'DE': '🇩🇪', 'FR': '🇫🇷', 'IN': '🇮🇳',
                'NG': '🇳🇬', 'ZA': '🇿🇦', 'UG': '🇺🇬', 'TZ': '🇹🇿'
            }
            flag = flag_map.get(obj.country_code, '🌍')
            return format_html(f'{flag} {obj.country_code}')
        return '🌍 Unknown'
    country_display.short_description = 'Country'
    
    def changelist_view(self, request, extra_context=None):
        """Add traffic statistics to the page view list"""
        extra_context = extra_context or {}
        
        # Get today's stats
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        today_views = AnonymousPageView.objects.filter(timestamp__date=today).count()
        yesterday_views = AnonymousPageView.objects.filter(timestamp__date=yesterday).count()
        week_views = AnonymousPageView.objects.filter(timestamp__date__gte=week_ago).count()
        
        # Unique visitors (anonymous IDs)
        today_visitors = AnonymousPageView.objects.filter(
            timestamp__date=today
        ).values('anonymous_id').distinct().count()
        
        week_visitors = AnonymousPageView.objects.filter(
            timestamp__date__gte=week_ago
        ).values('anonymous_id').distinct().count()
        
        # Popular pages this week
        popular_pages = AnonymousPageView.objects.filter(
            timestamp__date__gte=week_ago
        ).values('path', 'page_category').annotate(
            views=Count('id')
        ).order_by('-views')[:5]
        
        # Device breakdown
        mobile_views = AnonymousPageView.objects.filter(
            timestamp__date__gte=week_ago,
            is_mobile=True
        ).count()
        
        mobile_percentage = (mobile_views / week_views * 100) if week_views > 0 else 0
        
        extra_context.update({
            'traffic_stats': {
                'today_views': today_views,
                'yesterday_views': yesterday_views,
                'views_change': today_views - yesterday_views,
                'today_visitors': today_visitors,
                'week_views': week_views,
                'week_visitors': week_visitors,
                'mobile_percentage': round(mobile_percentage, 1),
                'popular_pages': popular_pages,
            }
        })
        
        return super().changelist_view(request, extra_context)


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    """
    Daily business metrics - see your growth!
    """
    
    list_display = [
        'date',
        'page_views_display',
        'visitors_display',
        'registrations_display',
        'mobile_percentage_display',
        'top_browser'
    ]
    
    list_filter = ['date', 'top_browser']
    
    date_hierarchy = 'date'
    
    readonly_fields = [
        'date',
        'total_page_views',
        'unique_sessions',
        'new_registrations',
        'trips_created',
        'mobile_percentage',
        'top_browser',
        'top_country'
    ]
    
    def has_add_permission(self, request):
        """Don't allow manual addition"""
        return False
    
    def page_views_display(self, obj):
        """Show page views with trend"""
        return format_html(
            '<strong style="color: #28a745;">{}</strong> views',
            obj.total_page_views
        )
    page_views_display.short_description = 'Page Views'
    
    def visitors_display(self, obj):
        """Show unique visitors"""
        return format_html(
            '<strong style="color: #007bff;">{}</strong> visitors',
            obj.unique_sessions
        )
    visitors_display.short_description = 'Visitors'
    
    def registrations_display(self, obj):
        """Show new registrations"""
        if obj.new_registrations > 0:
            return format_html(
                '<strong style="color: #ffc107;">{}</strong> new users',
                obj.new_registrations
            )
        return '0 new users'
    registrations_display.short_description = 'New Users'
    
    def mobile_percentage_display(self, obj):
        """Show mobile percentage with icon"""
        return format_html(
            '<i class="bi bi-phone"></i> {}%',
            round(obj.mobile_percentage, 1)
        )
    mobile_percentage_display.short_description = 'Mobile %'


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    """
    User consent tracking - legal compliance
    """
    
    list_display = [
        'user_display',
        'consent_type',
        'status_display',
        'consent_timestamp'
    ]
    
    list_filter = [
        'consent_type',
        'granted',
        'withdrawn',
        'consent_timestamp'
    ]
    
    search_fields = ['user__username', 'user__email']
    
    readonly_fields = [
        'user',
        'session_key',
        'consent_type',
        'granted',
        'consent_timestamp',
        'ip_address',
        'user_agent',
        'withdrawn',
        'withdrawn_at'
    ]
    
    def has_add_permission(self, request):
        """Don't allow manual addition"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make read-only"""
        return False
    
    def user_display(self, obj):
        """Show user or anonymous session"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email
            )
        return format_html(
            '<em>Anonymous</em><br><small>Session: {}</small>',
            obj.session_key[:8] + '...'
        )
    user_display.short_description = 'User'
    
    def status_display(self, obj):
        """Show consent status with colors"""
        if obj.withdrawn:
            return format_html(
                '<span style="color: #dc3545;">❌ Withdrawn</span>'
            )
        elif obj.granted:
            return format_html(
                '<span style="color: #28a745;">✅ Granted</span>'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">❌ Denied</span>'
            )
    status_display.short_description = 'Status'


# Custom admin site title
admin.site.site_header = "SafariSmart Kenya Analytics"
admin.site.site_title = "SafariSmart Analytics"
admin.site.index_title = "Website Traffic & Business Metrics"