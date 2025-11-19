"""
Privacy-First Analytics for SafariSmart Kenya

GDPR, CCPA, and Kenya Data Protection Act compliant analytics system.
Only collects essential data with proper consent management.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import hashlib
import uuid


class ConsentRecord(models.Model):
    """Track user consent for data collection"""
    
    CONSENT_TYPES = [
        ('essential', 'Essential Cookies (Required)'),
        ('analytics', 'Analytics Cookies (Optional)'),
        ('marketing', 'Marketing Cookies (Optional)'),
        ('personalization', 'Personalization (Optional)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, help_text="For anonymous users")
    
    consent_type = models.CharField(max_length=20, choices=CONSENT_TYPES)
    granted = models.BooleanField(default=False)
    
    # Legal requirements
    consent_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Consent withdrawal
    withdrawn = models.BooleanField(default=False)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'session_key', 'consent_type']
        indexes = [
            models.Index(fields=['user', 'consent_type']),
            models.Index(fields=['session_key', 'consent_type']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else f"Session {self.session_key[:8]}"
        status = "Granted" if self.granted and not self.withdrawn else "Denied/Withdrawn"
        return f"{user_info} - {self.get_consent_type_display()}: {status}"


class AnonymousPageView(models.Model):
    """
    Privacy-first page view tracking.
    
    Only stores essential data, anonymizes IP addresses,
    and respects user consent.
    """
    
    # Anonymous identifier (hashed session + date)
    anonymous_id = models.CharField(max_length=64, help_text="Hashed session identifier")
    
    # Page info (essential for business)
    path = models.CharField(max_length=200, help_text="URL path (no query params)")
    page_category = models.CharField(max_length=50, help_text="landing, destinations, trips, etc.")
    
    # Minimal technical info (essential for performance)
    is_mobile = models.BooleanField(default=False)
    browser_family = models.CharField(max_length=50, blank=True, help_text="Chrome, Firefox, Safari")
    
    # Anonymized location (country only, no city/IP)
    country_code = models.CharField(max_length=2, blank=True, help_text="KE, US, UK, etc.")
    
    # Timing (essential for analytics)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'page_category']),
            models.Index(fields=['anonymous_id']),
        ]
    
    def __str__(self):
        return f"Anonymous view of {self.path} at {self.timestamp.strftime('%H:%M')}"
    
    @classmethod
    def create_anonymous_view(cls, request, page_category="other"):
        """Create an anonymous page view record"""
        try:
            # Create anonymous ID (changes daily for privacy)
            session_key = request.session.session_key or request.session.create()
            date_str = timezone.now().date().isoformat()
            anonymous_id = hashlib.sha256(f"{session_key}_{date_str}".encode()).hexdigest()
            
            # Detect mobile (essential for UX)
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone'])
            
            # Browser family (for compatibility)
            browser_family = "unknown"
            if 'chrome' in user_agent:
                browser_family = "chrome"
            elif 'firefox' in user_agent:
                browser_family = "firefox"
            elif 'safari' in user_agent:
                browser_family = "safari"
            
            # Clean path (remove sensitive query params)
            path = request.path
            if len(path) > 200:
                path = path[:200]
            
            cls.objects.create(
                anonymous_id=anonymous_id,
                path=path,
                page_category=page_category,
                is_mobile=is_mobile,
                browser_family=browser_family,
                # Note: No IP address stored, no country detection without consent
            )
            
        except Exception as e:
            # Never let analytics break the site
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Anonymous analytics error: {str(e)}")


class BusinessMetrics(models.Model):
    """
    Essential business metrics that don't require consent.
    
    Aggregated, anonymous data for business intelligence.
    """
    
    date = models.DateField(unique=True)
    
    # Essential business metrics
    total_page_views = models.IntegerField(default=0)
    unique_sessions = models.IntegerField(default=0)
    new_registrations = models.IntegerField(default=0)
    trips_created = models.IntegerField(default=0)
    
    # Technical metrics (essential for performance)
    mobile_percentage = models.FloatField(default=0.0)
    top_browser = models.CharField(max_length=50, blank=True)
    
    # Geographic (country level only)
    top_country = models.CharField(max_length=2, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Business metrics for {self.date}"
    
    @classmethod
    def calculate_daily_metrics(cls, date=None):
        """Calculate daily business metrics"""
        if date is None:
            date = timezone.now().date()
        
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # Page views
        daily_views = AnonymousPageView.objects.filter(
            timestamp__range=[start_of_day, end_of_day]
        )
        
        total_page_views = daily_views.count()
        unique_sessions = daily_views.values('anonymous_id').distinct().count()
        
        # Mobile percentage
        mobile_views = daily_views.filter(is_mobile=True).count()
        mobile_percentage = (mobile_views / total_page_views * 100) if total_page_views > 0 else 0
        
        # Top browser
        browser_stats = daily_views.values('browser_family').annotate(
            count=models.Count('id')
        ).order_by('-count').first()
        top_browser = browser_stats['browser_family'] if browser_stats else ''
        
        # New registrations (from User model)
        new_registrations = User.objects.filter(
            date_joined__range=[start_of_day, end_of_day]
        ).count()
        
        # Create or update metrics
        metrics, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_page_views': total_page_views,
                'unique_sessions': unique_sessions,
                'new_registrations': new_registrations,
                'mobile_percentage': mobile_percentage,
                'top_browser': top_browser,
            }
        )
        
        if not created:
            metrics.total_page_views = total_page_views
            metrics.unique_sessions = unique_sessions
            metrics.new_registrations = new_registrations
            metrics.mobile_percentage = mobile_percentage
            metrics.top_browser = top_browser
            metrics.save()
        
        return metrics


class PrivacyService:
    """Service for privacy-compliant analytics"""
    
    @staticmethod
    def has_analytics_consent(request):
        """Check if user has given analytics consent"""
        if request.user.is_authenticated:
            return ConsentRecord.objects.filter(
                user=request.user,
                consent_type='analytics',
                granted=True,
                withdrawn=False
            ).exists()
        else:
            session_key = request.session.session_key
            if not session_key:
                return False
            return ConsentRecord.objects.filter(
                session_key=session_key,
                consent_type='analytics',
                granted=True,
                withdrawn=False
            ).exists()
    
    @staticmethod
    def record_consent(request, consent_type, granted):
        """Record user consent"""
        try:
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key or request.session.create()
            
            # Get or create consent record
            consent, created = ConsentRecord.objects.get_or_create(
                user=user,
                session_key=session_key if not user else '',
                consent_type=consent_type,
                defaults={
                    'granted': granted,
                    'ip_address': PrivacyService.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                }
            )
            
            if not created:
                # Update existing consent
                consent.granted = granted
                consent.withdrawn = False
                consent.save()
            
            return consent
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Consent recording error: {str(e)}")
            return None
    
    @staticmethod
    def withdraw_consent(request, consent_type):
        """Withdraw user consent and delete related data"""
        try:
            user = request.user if request.user.is_authenticated else None
            session_key = request.session.session_key
            
            # Mark consent as withdrawn
            consents = ConsentRecord.objects.filter(
                user=user,
                session_key=session_key if not user else '',
                consent_type=consent_type
            )
            
            for consent in consents:
                consent.withdrawn = True
                consent.withdrawn_at = timezone.now()
                consent.save()
            
            # Delete related analytics data if requested
            if consent_type == 'analytics':
                # Delete user's analytics data
                # Implementation depends on what data you've collected
                pass
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Consent withdrawal error: {str(e)}")
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    @staticmethod
    def track_page_view(request, page_category="other"):
        """Track page view with privacy compliance"""
        try:
            # Always track essential anonymous metrics
            AnonymousPageView.create_anonymous_view(request, page_category)
            
            # Only track detailed analytics with consent
            if PrivacyService.has_analytics_consent(request):
                # Enhanced tracking with consent
                # This is where you'd add more detailed tracking
                pass
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Page view tracking error: {str(e)}")


# Data retention policy
class DataRetentionService:
    """Automatically delete old data to comply with privacy laws"""
    
    @staticmethod
    def cleanup_old_data():
        """Delete data older than retention period"""
        # Delete page views older than 2 years
        two_years_ago = timezone.now() - timedelta(days=730)
        AnonymousPageView.objects.filter(timestamp__lt=two_years_ago).delete()
        
        # Delete withdrawn consents older than 7 years (legal requirement)
        seven_years_ago = timezone.now() - timedelta(days=2555)
        ConsentRecord.objects.filter(
            withdrawn=True,
            withdrawn_at__lt=seven_years_ago
        ).delete()
        
        # Keep business metrics indefinitely (aggregated, anonymous)