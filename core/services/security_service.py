"""
Module: services/security_service.py
Purpose: Security service for accessing security settings

This module provides a centralized service for accessing security
settings from the database with caching.

 
"""

import logging
from typing import Optional, List
from django.core.cache import cache
from core.models_security import SecuritySettings, SecurityEvent

logger = logging.getLogger('core.security')


class SecurityService:
    """
    Singleton service for security settings and operations.
    
    Provides cached access to security settings and helper methods
    for security operations.
    
    Example:
        >>> security = SecurityService.get_instance()
        >>> if security.is_brute_force_enabled():
        ...     max_attempts = security.get_max_login_attempts()
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    @classmethod
    def get_instance(cls) -> 'SecurityService':
        """Get singleton instance."""
        return cls()
        
    def get_settings(self) -> SecuritySettings:
        """
        Get security settings (cached).
        
        Returns:
            SecuritySettings: Current security settings
        """
        return SecuritySettings.get_settings()
        
    # ==========================================================================
    # BRUTE FORCE PROTECTION
    # ==========================================================================
    
    def is_brute_force_enabled(self) -> bool:
        """Check if brute force protection is enabled."""
        return self.get_settings().brute_force_enabled
        
    def get_max_login_attempts(self) -> int:
        """Get maximum login attempts before lockout."""
        return self.get_settings().max_login_attempts
        
    def get_lockout_duration_minutes(self) -> int:
        """Get lockout duration in minutes."""
        return self.get_settings().lockout_duration_minutes
        
    # ==========================================================================
    # RATE LIMITING
    # ==========================================================================
    
    def is_global_rate_limit_enabled(self) -> bool:
        """Check if global rate limiting is enabled."""
        return self.get_settings().global_rate_limit_enabled
        
    def get_global_rate_limit_per_minute(self) -> int:
        """Get global rate limit per minute."""
        return self.get_settings().global_rate_limit_per_minute
        
    def get_api_rate_limit_per_minute(self) -> int:
        """Get API rate limit per minute."""
        return self.get_settings().api_rate_limit_per_minute
        
    def get_api_rate_limit_per_hour(self) -> int:
        """Get API rate limit per hour."""
        return self.get_settings().api_rate_limit_per_hour
        
    def get_api_rate_limit_per_day(self) -> int:
        """Get API rate limit per day."""
        return self.get_settings().api_rate_limit_per_day
        
    # ==========================================================================
    # SESSION SECURITY
    # ==========================================================================
    
    def get_session_timeout_minutes(self) -> int:
        """Get session timeout in minutes."""
        return self.get_settings().session_timeout_minutes
        
    def should_expire_session_on_close(self) -> bool:
        """Check if session should expire on browser close."""
        return self.get_settings().session_expire_on_close
        
    def should_require_https_cookies(self) -> bool:
        """Check if HTTPS is required for cookies."""
        return self.get_settings().require_https_cookies
        
    def should_validate_session_ip(self) -> bool:
        """Check if session IP should be validated."""
        return self.get_settings().validate_session_ip
        
    def should_validate_session_user_agent(self) -> bool:
        """Check if session user agent should be validated."""
        return self.get_settings().validate_session_user_agent
        
    # ==========================================================================
    # PASSWORD SECURITY
    # ==========================================================================
    
    def get_min_password_length(self) -> int:
        """Get minimum password length."""
        return self.get_settings().min_password_length
        
    def should_require_uppercase(self) -> bool:
        """Check if uppercase letters are required."""
        return self.get_settings().require_uppercase
        
    def should_require_lowercase(self) -> bool:
        """Check if lowercase letters are required."""
        return self.get_settings().require_lowercase
        
    def should_require_numbers(self) -> bool:
        """Check if numbers are required."""
        return self.get_settings().require_numbers
        
    def should_require_special_chars(self) -> bool:
        """Check if special characters are required."""
        return self.get_settings().require_special_chars
        
    def get_password_expiry_days(self) -> int:
        """Get password expiry in days (0 = never)."""
        return self.get_settings().password_expiry_days
        
    # ==========================================================================
    # ADMIN SECURITY
    # ==========================================================================
    
    def is_admin_ip_whitelist_enabled(self) -> bool:
        """Check if admin IP whitelist is enabled."""
        return self.get_settings().admin_ip_whitelist_enabled
        
    def get_admin_allowed_ips(self) -> List[str]:
        """Get list of allowed admin IPs."""
        return self.get_settings().get_admin_allowed_ips_list()
        
    def get_admin_session_timeout_minutes(self) -> int:
        """Get admin session timeout in minutes."""
        return self.get_settings().admin_session_timeout_minutes
        
    def is_ip_allowed_for_admin(self, ip_address: str) -> bool:
        """
        Check if IP is allowed to access admin.
        
        Args:
            ip_address (str): IP address to check
            
        Returns:
            bool: True if allowed or whitelist disabled
        """
        if not self.is_admin_ip_whitelist_enabled():
            return True
            
        allowed_ips = self.get_admin_allowed_ips()
        return ip_address in allowed_ips
        
    # ==========================================================================
    # SECURITY HEADERS
    # ==========================================================================
    
    def is_hsts_enabled(self) -> bool:
        """Check if HSTS is enabled."""
        return self.get_settings().enable_hsts
        
    def get_hsts_max_age_seconds(self) -> int:
        """Get HSTS max age in seconds."""
        return self.get_settings().hsts_max_age_seconds
        
    def is_csp_enabled(self) -> bool:
        """Check if CSP is enabled."""
        return self.get_settings().enable_csp
        
    def is_xss_protection_enabled(self) -> bool:
        """Check if XSS protection is enabled."""
        return self.get_settings().enable_xss_protection
        
    def is_clickjacking_protection_enabled(self) -> bool:
        """Check if clickjacking protection is enabled."""
        return self.get_settings().enable_clickjacking_protection
        
    # ==========================================================================
    # MONITORING & ALERTS
    # ==========================================================================
    
    def is_security_logging_enabled(self) -> bool:
        """Check if security logging is enabled."""
        return self.get_settings().enable_security_logging
        
    def is_failed_login_alerts_enabled(self) -> bool:
        """Check if failed login alerts are enabled."""
        return self.get_settings().enable_failed_login_alerts
        
    def get_failed_login_alert_threshold(self) -> int:
        """Get failed login alert threshold."""
        return self.get_settings().failed_login_alert_threshold
        
    def is_suspicious_activity_alerts_enabled(self) -> bool:
        """Check if suspicious activity alerts are enabled."""
        return self.get_settings().enable_suspicious_activity_alerts
        
    def get_alert_email(self) -> Optional[str]:
        """Get security alert email."""
        email = self.get_settings().alert_email
        return email if email else None
        
    # ==========================================================================
    # EVENT LOGGING
    # ==========================================================================
    
    def log_security_event(
        self,
        event_type: str,
        description: str,
        severity: str = 'medium',
        **kwargs
    ) -> Optional[SecurityEvent]:
        """
        Log a security event.
        
        Args:
            event_type (str): Type of event
            description (str): Event description
            severity (str): Severity level (low, medium, high, critical)
            **kwargs: Additional fields
            
        Returns:
            SecurityEvent: Created event or None if logging disabled
        """
        if not self.is_security_logging_enabled():
            return None
            
        try:
            return SecurityEvent.log_event(
                event_type=event_type,
                description=description,
                severity=severity,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
            return None
            
    def log_failed_login(
        self,
        username: str,
        ip_address: str,
        user_agent: str = ''
    ):
        """Log failed login attempt."""
        self.log_security_event(
            event_type='failed_login',
            severity='medium',
            description=f'Failed login attempt for user: {username}',
            user=username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
    def log_successful_login(
        self,
        username: str,
        ip_address: str,
        user_agent: str = ''
    ):
        """Log successful login."""
        self.log_security_event(
            event_type='successful_login',
            severity='low',
            description=f'Successful login for user: {username}',
            user=username,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
    def log_account_locked(
        self,
        username: str,
        ip_address: str,
        attempts: int
    ):
        """Log account lockout."""
        self.log_security_event(
            event_type='account_locked',
            severity='high',
            description=f'Account locked for user: {username} after {attempts} failed attempts',
            user=username,
            ip_address=ip_address,
            details={'attempts': attempts}
        )
        
    def log_suspicious_activity(
        self,
        description: str,
        ip_address: str,
        path: str = '',
        details: dict = None
    ):
        """Log suspicious activity."""
        self.log_security_event(
            event_type='suspicious_activity',
            severity='high',
            description=description,
            ip_address=ip_address,
            path=path,
            details=details or {}
        )
        
    def log_rate_limit_exceeded(
        self,
        ip_address: str,
        limit_type: str,
        count: int
    ):
        """Log rate limit violation."""
        self.log_security_event(
            event_type='rate_limit_exceeded',
            severity='medium',
            description=f'Rate limit exceeded: {limit_type}',
            ip_address=ip_address,
            details={'limit_type': limit_type, 'count': count}
        )
