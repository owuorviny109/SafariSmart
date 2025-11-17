"""
Custom security middleware for SafariSmart Kenya.

Provides additional security layers beyond Django's built-in protection.

Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

import logging
import hashlib
import time
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('core.security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add additional security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: Various restrictions
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS filter
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy (restrict dangerous features)
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'magnetometer=(), '
            'gyroscope=()'
        )
        
        return response


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validate incoming requests for suspicious patterns.
    
    Checks for:
    - Suspicious user agents
    - Known attack patterns
    - Malformed requests
    - SQL injection attempts
    - XSS attempts
    """
    
    # Suspicious patterns to detect
    SUSPICIOUS_PATTERNS = [
        'union select',
        'drop table',
        'insert into',
        'delete from',
        '<script',
        'javascript:',
        'onerror=',
        'onload=',
        '../',
        '..\\',
        '/etc/passwd',
        'cmd.exe',
        'powershell',
    ]
    
    # Suspicious user agents
    SUSPICIOUS_USER_AGENTS = [
        'sqlmap',
        'nikto',
        'nmap',
        'masscan',
        'metasploit',
        'burp',
        'acunetix',
        'nessus',
    ]
    
    def process_request(self, request):
        """Validate request before processing."""
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Check for suspicious user agents
        for suspicious_ua in self.SUSPICIOUS_USER_AGENTS:
            if suspicious_ua in user_agent:
                logger.warning(
                    f"Suspicious user agent detected: {user_agent} "
                    f"from IP: {self.get_client_ip(request)}"
                )
                return HttpResponseForbidden("Access denied")
        
        # Check request path for suspicious patterns
        path = request.path.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if pattern in path:
                logger.warning(
                    f"Suspicious pattern in path: {pattern} "
                    f"from IP: {self.get_client_ip(request)}"
                )
                return HttpResponseForbidden("Access denied")
        
        # Check query parameters
        for key, value in request.GET.items():
            value_str = str(value).lower()
            for pattern in self.SUSPICIOUS_PATTERNS:
                if pattern in value_str:
                    logger.warning(
                        f"Suspicious pattern in query param: {pattern} "
                        f"from IP: {self.get_client_ip(request)}"
                    )
                    return HttpResponseForbidden("Access denied")
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware.
    
    Limits requests per IP address to prevent abuse.
    Works in addition to the API rate limiter.
    """
    
    def process_request(self, request):
        """Check rate limit for IP."""
        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Create cache key
        cache_key = f'rate_limit:{ip}:{int(time.time() / 60)}'
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        # Check if rate limit exceeded
        max_requests = getattr(settings, 'GLOBAL_RATE_LIMIT_PER_MINUTE', 100)
        if count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for IP: {ip} "
                f"({count} requests in last minute)"
            )
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, count + 1, 70)  # 70 seconds (minute + buffer)
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security.
    
    Features:
    - Session fixation protection
    - Session hijacking detection
    - IP address validation
    - User agent validation
    """
    
    def process_request(self, request):
        """Validate session security."""
        if not request.user.is_authenticated:
            return None
        
        # Get current IP and user agent
        current_ip = self.get_client_ip(request)
        current_ua = request.META.get('HTTP_USER_AGENT', '')
        
        # Get stored values from session
        stored_ip = request.session.get('_security_ip')
        stored_ua = request.session.get('_security_ua')
        
        # First time - store values
        if not stored_ip:
            request.session['_security_ip'] = current_ip
            request.session['_security_ua'] = self.hash_ua(current_ua)
            return None
        
        # Validate IP address (allow some flexibility for mobile users)
        if stored_ip != current_ip:
            logger.warning(
                f"Session IP mismatch for user {request.user.username}: "
                f"stored={stored_ip}, current={current_ip}"
            )
            # Don't block, but log for monitoring
            # In production, you might want to force re-authentication
        
        # Validate user agent
        if stored_ua != self.hash_ua(current_ua):
            logger.warning(
                f"Session user agent mismatch for user {request.user.username}"
            )
            # Force re-authentication on user agent change
            from django.contrib.auth import logout
            logout(request)
            return HttpResponseForbidden(
                "Session security validation failed. Please login again."
            )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def hash_ua(user_agent):
        """Hash user agent for storage."""
        return hashlib.sha256(user_agent.encode()).hexdigest()


class AdminIPWhitelistMiddleware(MiddlewareMixin):
    """
    Restrict admin access to whitelisted IP addresses.
    
    Configure ADMIN_ALLOWED_IPS in settings.
    """
    
    def process_request(self, request):
        """Check if IP is allowed to access admin."""
        # Only check admin URLs
        admin_url = getattr(settings, 'ADMIN_URL', 'admin/')
        if not request.path.startswith(f'/{admin_url}'):
            return None
        
        # Get allowed IPs from settings
        allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', [])
        
        # If no whitelist configured, allow all (development mode)
        if not allowed_ips:
            return None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check if IP is allowed
        if client_ip not in allowed_ips:
            logger.warning(
                f"Unauthorized admin access attempt from IP: {client_ip}"
            )
            return HttpResponseForbidden(
                "Access to admin panel is restricted."
            )
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityAuditMiddleware(MiddlewareMixin):
    """
    Log security-relevant events for audit trail.
    
    Logs:
    - Login attempts
    - Admin access
    - Failed authentications
    - Suspicious activity
    """
    
    def process_request(self, request):
        """Log security events."""
        # Log admin access
        admin_url = getattr(settings, 'ADMIN_URL', 'admin/')
        if request.path.startswith(f'/{admin_url}'):
            logger.info(
                f"Admin access: {request.user.username if request.user.is_authenticated else 'anonymous'} "
                f"from IP: {self.get_client_ip(request)} "
                f"path: {request.path}"
            )
        
        # Log authentication endpoints
        auth_paths = ['/login/', '/register/', '/password-reset/']
        if any(request.path.startswith(path) for path in auth_paths):
            logger.info(
                f"Auth endpoint access: {request.path} "
                f"from IP: {self.get_client_ip(request)}"
            )
        
        return None
    
    def process_response(self, request, response):
        """Log response status for security events."""
        # Log 403 Forbidden responses
        if response.status_code == 403:
            logger.warning(
                f"403 Forbidden: {request.path} "
                f"from IP: {self.get_client_ip(request)} "
                f"user: {request.user.username if request.user.is_authenticated else 'anonymous'}"
            )
        
        # Log 401 Unauthorized responses
        if response.status_code == 401:
            logger.warning(
                f"401 Unauthorized: {request.path} "
                f"from IP: {self.get_client_ip(request)}"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
