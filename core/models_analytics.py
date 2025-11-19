"""
Analytics Models for SafariSmart Kenya

Track user behavior, page views, and business metrics.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class PageView(models.Model):
    """Track every page view on the site"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, help_text="Anonymous user session")
    
    # Page info
    path = models.CharField(max_length=500, help_text="URL path visited")
    page_title = models.CharField(max_length=200, blank=True)
    referrer = models.URLField(blank=True, help_text="Where user came from")
    
    # User info
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(help_text="Browser and device info")
    
    # Geographic info (can be populated by IP lookup)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    time_on_page = models.IntegerField(null=True, blank=True, help_text="Seconds spent on page")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Anonymous ({self.session_key[:8]})"
        return f"{user_info} visited {self.path} at {self.timestamp.strftime('%H:%M')}"


class UserActivity(models.Model):
    """Track important user actions"""
    
    ACTION_CHOICES = [
        ('register', 'User Registration'),
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('trip_created', 'Trip Created'),
        ('trip_saved', 'Trip Saved'),
        ('trip_shared', 'Trip Shared'),
        ('destination_viewed', 'Destination Viewed'),
        ('search_performed', 'Search Performed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, help_text="Additional action data")
    
    # Context
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class DailyStats(models.Model):
    """Daily aggregated statistics"""
    
    date = models.DateField(unique=True)
    
    # Traffic stats
    total_page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    returning_users = models.IntegerField(default=0)
    
    # Business stats
    trips_created = models.IntegerField(default=0)
    trips_saved = models.IntegerField(default=0)
    destinations_viewed = models.IntegerField(default=0)
    
    # Engagement stats
    avg_session_duration = models.FloatField(default=0.0, help_text="Average minutes per session")
    bounce_rate = models.FloatField(default=0.0, help_text="Percentage of single-page sessions")
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date} - {self.unique_visitors} visitors"
    
    @classmethod
    def calculate_for_date(cls, date):
        """Calculate and save stats for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # Page view stats
        page_views = PageView.objects.filter(
            timestamp__range=[start_of_day, end_of_day]
        )
        
        total_page_views = page_views.count()
        unique_visitors = page_views.values('session_key').distinct().count()
        
        # User stats
        new_users = UserActivity.objects.filter(
            action='register',
            timestamp__range=[start_of_day, end_of_day]
        ).count()
        
        # Business stats
        trips_created = UserActivity.objects.filter(
            action='trip_created',
            timestamp__range=[start_of_day, end_of_day]
        ).count()
        
        trips_saved = UserActivity.objects.filter(
            action='trip_saved',
            timestamp__range=[start_of_day, end_of_day]
        ).count()
        
        # Create or update daily stats
        stats, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_page_views': total_page_views,
                'unique_visitors': unique_visitors,
                'new_users': new_users,
                'trips_created': trips_created,
                'trips_saved': trips_saved,
            }
        )
        
        if not created:
            # Update existing stats
            stats.total_page_views = total_page_views
            stats.unique_visitors = unique_visitors
            stats.new_users = new_users
            stats.trips_created = trips_created
            stats.trips_saved = trips_saved
            stats.save()
        
        return stats


class AnalyticsService:
    """Service for tracking and retrieving analytics"""
    
    @staticmethod
    def track_page_view(request, page_title=""):
        """Track a page view"""
        try:
            # Get user info
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key or request.session.create()
            
            # Get IP address
            ip_address = AnalyticsService.get_client_ip(request)
            
            # Create page view record
            PageView.objects.create(
                user=user,
                session_key=session_key,
                path=request.path,
                page_title=page_title,
                referrer=request.META.get('HTTP_REFERER', ''),
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        except Exception as e:
            # Don't let analytics break the site
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Analytics tracking error: {str(e)}")
    
    @staticmethod
    def track_user_activity(user, action, details=None, request=None):
        """Track user activity"""
        try:
            ip_address = '127.0.0.1'
            user_agent = ''
            
            if request:
                ip_address = AnalyticsService.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            UserActivity.objects.create(
                user=user,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"User activity tracking error: {str(e)}")
    
    @staticmethod
    def get_client_ip(request):
        """Get the real IP address of the client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    @staticmethod
    def get_dashboard_stats():
        """Get stats for admin dashboard"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # Today's stats
        today_views = PageView.objects.filter(timestamp__date=today).count()
        today_users = PageView.objects.filter(timestamp__date=today).values('session_key').distinct().count()
        
        # Yesterday's stats for comparison
        yesterday_views = PageView.objects.filter(timestamp__date=yesterday).count()
        yesterday_users = PageView.objects.filter(timestamp__date=yesterday).values('session_key').distinct().count()
        
        # Week stats
        week_views = PageView.objects.filter(timestamp__date__gte=week_ago).count()
        week_users = PageView.objects.filter(timestamp__date__gte=week_ago).values('session_key').distinct().count()
        
        # Popular pages
        popular_pages = PageView.objects.filter(
            timestamp__date__gte=week_ago
        ).values('path').annotate(
            views=models.Count('id')
        ).order_by('-views')[:10]
        
        return {
            'today': {
                'views': today_views,
                'users': today_users,
                'views_change': today_views - yesterday_views,
                'users_change': today_users - yesterday_users,
            },
            'week': {
                'views': week_views,
                'users': week_users,
            },
            'popular_pages': popular_pages,
        }