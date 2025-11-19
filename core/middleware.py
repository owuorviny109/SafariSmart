"""
Analytics Middleware for SafariSmart Kenya

Automatically tracks page views in a privacy-compliant way.
"""

from .models_privacy_analytics import PrivacyService


class AnalyticsMiddleware:
    """
    Middleware to automatically track page views.
    
    Only tracks essential, anonymous data that's legal without consent.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Track page view after response (non-blocking)
        if self.should_track(request):
            try:
                page_category = self.get_page_category(request.path)
                PrivacyService.track_page_view(request, page_category)
            except Exception as e:
                # Never let analytics break the site
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Analytics middleware error: {str(e)}")
        
        return response
    
    def should_track(self, request):
        """Determine if we should track this request"""
        # Don't track admin pages
        if request.path.startswith('/admin/'):
            return False
        
        # Don't track API endpoints
        if request.path.startswith('/api/'):
            return False
        
        # Don't track static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        
        # Don't track robots.txt, sitemap, etc.
        if request.path in ['/robots.txt', '/sitemap.xml', '/favicon.ico']:
            return False
        
        # Only track GET requests
        if request.method != 'GET':
            return False
        
        return True
    
    def get_page_category(self, path):
        """Categorize pages for better analytics"""
        if path == '/':
            return 'landing'
        elif path.startswith('/destinations/'):
            return 'destinations'
        elif path.startswith('/itinerary/') or path.startswith('/trip/'):
            return 'trips'
        elif path.startswith('/dashboard/'):
            return 'dashboard'
        elif path.startswith('/accounts/'):
            return 'auth'
        elif path.startswith('/wizard/'):
            return 'wizard'
        else:
            return 'other'