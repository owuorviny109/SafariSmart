"""
Security settings for SafariSmart Kenya.

This file contains all security-related configurations.
Import this in settings.py for production.

Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from decouple import config

# =============================================================================
# CRITICAL SECURITY SETTINGS
# =============================================================================

# HTTPS/SSL Configuration
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTP Strict Transport Security (HSTS)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# SESSION SECURITY
# =============================================================================

SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=3600, cast=int)  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = config('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=False, cast=bool)

# =============================================================================
# CSRF PROTECTION
# =============================================================================

CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_AGE = 3600  # 1 hour

# =============================================================================
# PASSWORD SECURITY
# =============================================================================

# Enhanced password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': config('PASSWORD_MIN_LENGTH', default=12, cast=int),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashing (Argon2 is most secure)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# =============================================================================
# CONTENT SECURITY POLICY (CSP)
# =============================================================================

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Required for Bootstrap
    "cdn.jsdelivr.net",
    "unpkg.com",  # For Leaflet
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Required for inline styles
    "cdn.jsdelivr.net",
    "unpkg.com",  # For Leaflet
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https:",
    "*.tile.openstreetmap.org",  # For map tiles
)
CSP_FONT_SRC = (
    "'self'",
    "cdn.jsdelivr.net",
)
CSP_CONNECT_SRC = (
    "'self'",
    "api.openweathermap.org",  # Weather API
)

# =============================================================================
# DJANGO-AXES (Brute Force Protection)
# =============================================================================

# Enable django-axes
AXES_ENABLED = config('AXES_ENABLED', default=True, cast=bool)

# Lock out after 5 failed attempts
AXES_FAILURE_LIMIT = config('AXES_FAILURE_LIMIT', default=5, cast=int)

# Lock out for 30 minutes
AXES_COOLOFF_TIME = config('AXES_COOLOFF_TIME', default=0.5, cast=float)  # hours

# Lock by IP and username combination
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True

# Reset attempts after successful login
AXES_RESET_ON_SUCCESS = True

# Use database for tracking
AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'

# Lockout template
AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'

# Lockout message
AXES_LOCKOUT_MESSAGE = 'Too many failed login attempts. Please try again later.'

# =============================================================================
# RATE LIMITING
# =============================================================================

# Django-ratelimit settings
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_VIEW = 'core.views.ratelimit_error'

# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================

# Maximum file upload size (5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Allowed file extensions
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.gif']

# File permissions
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# =============================================================================
# SECURITY LOGGING
# =============================================================================

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security.csrf': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['security'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core.security': {
            'handlers': ['security'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# ADMIN SECURITY
# =============================================================================

# Require HTTPS for admin
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Admin session timeout (15 minutes)
ADMIN_SESSION_TIMEOUT = 900

# =============================================================================
# API SECURITY
# =============================================================================

# API rate limiting (already implemented in core.services.rate_limiter)
API_RATE_LIMIT_PER_MINUTE = config('API_RATE_LIMIT_PER_MINUTE', default=60, cast=int)
API_RATE_LIMIT_PER_HOUR = config('API_RATE_LIMIT_PER_HOUR', default=1000, cast=int)
API_RATE_LIMIT_PER_DAY = config('API_RATE_LIMIT_PER_DAY', default=10000, cast=int)

# =============================================================================
# CORS SETTINGS (if API is public)
# =============================================================================

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
)

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# SECURITY MIDDLEWARE ORDER (Important!)
# =============================================================================

SECURITY_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',  # Brute force protection
    'csp.middleware.CSPMiddleware',  # Content Security Policy
]

# =============================================================================
# SECURITY CHECKLIST
# =============================================================================

"""
Production Security Checklist:

1. Environment Variables:
   - SECRET_KEY: Strong 50+ character random string
   - DEBUG: False
   - ALLOWED_HOSTS: Your domain(s)
   - SECURE_SSL_REDIRECT: True
   - SESSION_COOKIE_SECURE: True
   - CSRF_COOKIE_SECURE: True

2. Database:
   - Use PostgreSQL (not SQLite)
   - Enable SSL connections
   - Strong database password
   - Regular backups

3. Dependencies:
   - Install: django-axes, django-csp, argon2-cffi
   - Keep all packages updated
   - Run: pip install -r requirements.txt

4. Server:
   - Use HTTPS (Let's Encrypt)
   - Configure firewall
   - Disable directory listing
   - Hide server version

5. Monitoring:
   - Check logs/security.log daily
   - Set up alerts for suspicious activity
   - Monitor failed login attempts
   - Track API usage

6. Backups:
   - Daily database backups
   - Weekly full backups
   - Test restore procedures
   - Offsite backup storage

7. Updates:
   - Monthly security updates
   - Quarterly dependency updates
   - Annual security audit
   - Penetration testing

8. Compliance:
   - GDPR compliance (if EU users)
   - Data protection policy
   - Privacy policy
   - Terms of service
"""
