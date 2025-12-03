"""
Module: core/models_security.py
Purpose: Security configuration models for admin management

This module provides database models for managing security settings
through the Django admin interface.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache


class SecuritySettings(models.Model):
    """
    Singleton model for security settings management.
    
    All security settings can be managed through Django admin.
    Changes take effect immediately via cache invalidation.
    
    Attributes:
        # Brute Force Protection
        brute_force_enabled: Enable/disable brute force protection
        max_login_attempts: Maximum failed login attempts before lockout
        lockout_duration_minutes: How long to lock account (minutes)
        
        # Rate Limiting
        global_rate_limit_enabled: Enable/disable global rate limiting
        global_rate_limit_per_minute: Requests per minute per IP
        api_rate_limit_per_minute: API requests per minute
        api_rate_limit_per_hour: API requests per hour
        api_rate_limit_per_day: API requests per day
        
        # Session Security
        session_timeout_minutes: Session timeout in minutes
        session_expire_on_close: Expire session when browser closes
        require_https_cookies: Require HTTPS for cookies
        
        # Password Security
        min_password_length: Minimum password length
        require_uppercase: Require uppercase letters
        require_lowercase: Require lowercase letters
        require_numbers: Require numbers
        require_special_chars: Require special characters
        password_expiry_days: Days before password expires (0 = never)
        
        # Admin Security
        admin_ip_whitelist_enabled: Enable IP whitelist for admin
        admin_allowed_ips: Comma-separated list of allowed IPs
        admin_session_timeout_minutes: Admin session timeout
        
        # Security Headers
        enable_hsts: Enable HTTP Strict Transport Security
        hsts_max_age_seconds: HSTS max age in seconds
        enable_csp: Enable Content Security Policy
        enable_xss_protection: Enable XSS protection header
        
        # Monitoring & Alerts
        enable_security_logging: Enable security event logging
        enable_failed_login_alerts: Alert on failed logins
        failed_login_alert_threshold: Alert after N failed attempts
        enable_suspicious_activity_alerts: Alert on suspicious activity
        alert_email: Email for security alerts
    """
    
    # Singleton pattern - only one instance allowed
    singleton_id = models.IntegerField(default=1, unique=True, editable=False)
    
    # ==========================================================================
    # BRUTE FORCE PROTECTION
    # ==========================================================================
    
    brute_force_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Brute Force Protection",
        help_text="Protect against brute force login attacks"
    )
    
    max_login_attempts = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Maximum Login Attempts",
        help_text="Lock account after this many failed attempts"
    )
    
    lockout_duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name="Lockout Duration (minutes)",
        help_text="How long to lock account after failed attempts"
    )
    
    # ==========================================================================
    # RATE LIMITING
    # ==========================================================================
    
    global_rate_limit_enabled = models.BooleanField(
        default=True,
        verbose_name="Enable Global Rate Limiting",
        help_text="Limit requests per IP address"
    )
    
    global_rate_limit_per_minute = models.IntegerField(
        default=100,
        validators=[MinValueValidator(10), MaxValueValidator(1000)],
        verbose_name="Global Rate Limit (per minute)",
        help_text="Maximum requests per minute per IP"
    )
    
    api_rate_limit_per_minute = models.IntegerField(
        default=60,
        validators=[MinValueValidator(10), MaxValueValidator(500)],
        verbose_name="API Rate Limit (per minute)",
        help_text="Maximum API requests per minute"
    )
    
    api_rate_limit_per_hour = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(100), MaxValueValidator(10000)],
        verbose_name="API Rate Limit (per hour)",
        help_text="Maximum API requests per hour"
    )
    
    api_rate_limit_per_day = models.IntegerField(
        default=10000,
        validators=[MinValueValidator(1000), MaxValueValidator(100000)],
        verbose_name="API Rate Limit (per day)",
        help_text="Maximum API requests per day"
    )
    
    # ==========================================================================
    # SESSION SECURITY
    # ==========================================================================
    
    session_timeout_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name="Session Timeout (minutes)",
        help_text="Automatically logout after this many minutes of inactivity"
    )
    
    session_expire_on_close = models.BooleanField(
        default=False,
        verbose_name="Expire Session on Browser Close",
        help_text="End session when user closes browser"
    )
    
    require_https_cookies = models.BooleanField(
        default=True,
        verbose_name="Require HTTPS for Cookies",
        help_text="Only send cookies over HTTPS (production only)"
    )
    
    validate_session_ip = models.BooleanField(
        default=True,
        verbose_name="Validate Session IP Address",
        help_text="Detect session hijacking by validating IP"
    )
    
    validate_session_user_agent = models.BooleanField(
        default=True,
        verbose_name="Validate Session User Agent",
        help_text="Detect session hijacking by validating browser"
    )
    
    # ==========================================================================
    # PASSWORD SECURITY
    # ==========================================================================
    
    min_password_length = models.IntegerField(
        default=12,
        validators=[MinValueValidator(8), MaxValueValidator(128)],
        verbose_name="Minimum Password Length",
        help_text="Minimum number of characters required"
    )
    
    require_uppercase = models.BooleanField(
        default=True,
        verbose_name="Require Uppercase Letters",
        help_text="Password must contain uppercase letters (A-Z)"
    )
    
    require_lowercase = models.BooleanField(
        default=True,
        verbose_name="Require Lowercase Letters",
        help_text="Password must contain lowercase letters (a-z)"
    )
    
    require_numbers = models.BooleanField(
        default=True,
        verbose_name="Require Numbers",
        help_text="Password must contain numbers (0-9)"
    )
    
    require_special_chars = models.BooleanField(
        default=True,
        verbose_name="Require Special Characters",
        help_text="Password must contain special characters (!@#$%^&*)"
    )
    
    password_expiry_days = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(365)],
        verbose_name="Password Expiry (days)",
        help_text="Force password change after N days (0 = never)"
    )
    
    # ==========================================================================
    # ADMIN SECURITY
    # ==========================================================================
    
    admin_ip_whitelist_enabled = models.BooleanField(
        default=False,
        verbose_name="Enable Admin IP Whitelist",
        help_text="Restrict admin access to specific IP addresses"
    )
    
    admin_allowed_ips = models.TextField(
        blank=True,
        verbose_name="Admin Allowed IPs",
        help_text="Comma-separated list of allowed IP addresses (e.g., 192.168.1.1, 10.0.0.1)"
    )
    
    admin_session_timeout_minutes = models.IntegerField(
        default=15,
        validators=[MinValueValidator(5), MaxValueValidator(120)],
        verbose_name="Admin Session Timeout (minutes)",
        help_text="Admin sessions timeout faster for security"
    )
    
    # ==========================================================================
    # SECURITY HEADERS
    # ==========================================================================
    
    enable_hsts = models.BooleanField(
        default=True,
        verbose_name="Enable HSTS",
        help_text="HTTP Strict Transport Security (force HTTPS)"
    )
    
    hsts_max_age_seconds = models.IntegerField(
        default=31536000,
        validators=[MinValueValidator(300), MaxValueValidator(63072000)],
        verbose_name="HSTS Max Age (seconds)",
        help_text="How long browsers should remember to use HTTPS (1 year = 31536000)"
    )
    
    enable_csp = models.BooleanField(
        default=True,
        verbose_name="Enable Content Security Policy",
        help_text="Prevent XSS and injection attacks"
    )
    
    enable_xss_protection = models.BooleanField(
        default=True,
        verbose_name="Enable XSS Protection",
        help_text="Enable browser XSS filter"
    )
    
    enable_clickjacking_protection = models.BooleanField(
        default=True,
        verbose_name="Enable Clickjacking Protection",
        help_text="Prevent site from being embedded in iframes"
    )
    
    # ==========================================================================
    # MONITORING & ALERTS
    # ==========================================================================
    
    enable_security_logging = models.BooleanField(
        default=True,
        verbose_name="Enable Security Logging",
        help_text="Log all security events"
    )
    
    enable_failed_login_alerts = models.BooleanField(
        default=True,
        verbose_name="Enable Failed Login Alerts",
        help_text="Send alerts for failed login attempts"
    )
    
    failed_login_alert_threshold = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Failed Login Alert Threshold",
        help_text="Send alert after this many failed attempts"
    )
    
    enable_suspicious_activity_alerts = models.BooleanField(
        default=True,
        verbose_name="Enable Suspicious Activity Alerts",
        help_text="Alert on suspicious patterns (SQL injection, XSS, etc.)"
    )
    
    alert_email = models.EmailField(
        blank=True,
        verbose_name="Security Alert Email",
        help_text="Email address for security alerts"
    )
    
    # ==========================================================================
    # METADATA
    # ==========================================================================
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    
    updated_by = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Updated By"
    )
    
    class Meta:
        verbose_name = "Security Settings"
        verbose_name_plural = "Security Settings"
        
    def __str__(self):
        return "Security Settings"
        
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton)."""
        self.singleton_id = 1
        # Clear cache when settings change
        cache.delete('security_settings')
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        """Prevent deletion of security settings."""
        pass
        
    @classmethod
    def get_settings(cls):
        """
        Get security settings (cached).
        
        Returns:
            SecuritySettings: The security settings instance
        """
        settings = cache.get('security_settings')
        if not settings:
            settings, _ = cls.objects.get_or_create(singleton_id=1)
            cache.set('security_settings', settings, 300)  # Cache for 5 minutes
        return settings
        
    def get_admin_allowed_ips_list(self):
        """
        Get admin allowed IPs as a list.
        
        Returns:
            list: List of allowed IP addresses
        """
        if not self.admin_allowed_ips:
            return []
        return [ip.strip() for ip in self.admin_allowed_ips.split(',') if ip.strip()]


class SecurityEvent(models.Model):
    """
    Log security events for monitoring and analysis.
    
    Tracks:
    - Failed login attempts
    - Suspicious activity
    - Rate limit violations
    - Session hijacking attempts
    - Admin access
    - Configuration changes
    """
    
    EVENT_TYPES = [
        ('failed_login', 'Failed Login'),
        ('successful_login', 'Successful Login'),
        ('account_locked', 'Account Locked'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('session_hijack_attempt', 'Session Hijack Attempt'),
        ('admin_access', 'Admin Access'),
        ('config_change', 'Configuration Change'),
        ('password_change', 'Password Change'),
        ('security_alert', 'Security Alert'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        db_index=True,
        verbose_name="Event Type"
    )
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_LEVELS,
        default='medium',
        db_index=True,
        verbose_name="Severity"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Timestamp"
    )
    
    user = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="User"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="IP Address"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Request Path"
    )
    
    description = models.TextField(
        verbose_name="Description"
    )
    
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Additional Details"
    )
    
    resolved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Resolved"
    )
    
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Resolved At"
    )
    
    resolved_by = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Resolved By"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
    @classmethod
    def log_event(cls, event_type, description, **kwargs):
        """
        Log a security event.
        
        Args:
            event_type (str): Type of event
            description (str): Event description
            **kwargs: Additional fields (severity, user, ip_address, etc.)
        """
        return cls.objects.create(
            event_type=event_type,
            description=description,
            **kwargs
        )
