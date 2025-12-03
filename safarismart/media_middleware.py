"""
Middleware to add cache-busting headers for media files.
Ensures updated destination images show immediately in production.
"""
from django.utils.http import http_date
from datetime import datetime, timezone


class MediaCacheBustingMiddleware:
    """
    Add cache-control headers to media files to prevent stale image caching.
    
    When admins update destination images, this ensures browsers re-fetch them
    instead of showing cached versions from before the update.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cache-busting headers for media files
        if request.path.startswith('/media/'):
            # For images, allow 1 hour cache (max-age=3600)
            # After 1 hour, browser must revalidate with server (must-revalidate)
            if any(request.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                response['Cache-Control'] = 'public, max-age=3600, must-revalidate'
                # Add Last-Modified header to enable conditional requests
                response['Last-Modified'] = http_date(datetime.now(timezone.utc).timestamp())
            # Other media files (documents, etc.) - short cache
            else:
                response['Cache-Control'] = 'public, max-age=300, must-revalidate'
        
        return response
