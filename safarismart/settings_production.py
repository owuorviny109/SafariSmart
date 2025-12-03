"""
Production settings for SafariSmart Kenya
"""
from .settings import *
import dj_database_url
import os

# Security Settings
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'temporary-secret-key-change-in-production')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.onrender.com,localhost').split(',')

# AI Generation Settings
# Set to False to use template generator (faster, no API calls)
ENABLE_AI_GENERATION = os.environ.get('ENABLE_AI_GENERATION', 'True') == 'True'

# CSRF Settings for production
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://safarismart.onrender.com',
]

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files - CRITICAL: Must be served for updated destination images to show
MEDIA_URL = '/media/'
# Use persistent Render disk for media storage (mounted at /var/www/media)
# This ensures uploaded images persist across app restarts
if os.environ.get('RENDER'):
    MEDIA_ROOT = '/var/www/media'
    # Ensure media directory exists
    try:
        os.makedirs(MEDIA_ROOT, exist_ok=True)
        # Also create destinations subdir to be safe
        os.makedirs(os.path.join(MEDIA_ROOT, 'destinations'), exist_ok=True)
    except Exception as e:
        print(f"Error creating media directory: {e}")

# WhiteNoise for static file serving - use custom storage that ignores missing source maps
STATICFILES_STORAGE = 'safarismart.storage.ForgivingManifestStaticFilesStorage'

# Add WhiteNoise to middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Add cache-busting middleware for media files
MIDDLEWARE.append('safarismart.media_middleware.MediaCacheBustingMiddleware')

# Security - Only enable SSL redirect if not in debug mode
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
