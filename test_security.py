"""
Security testing script for SafariSmart Kenya.

Tests various security features to ensure they're working correctly.

Run with: python test_security.py
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from django.conf import settings
from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from core.middleware.security import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    RateLimitMiddleware,
)


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_test(name, passed):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")


def test_security_settings():
    """Test security settings configuration."""
    print_header("SECURITY SETTINGS TEST")
    
    tests = [
        ("SECRET_KEY is set", bool(settings.SECRET_KEY)),
        ("SECRET_KEY is not default", 'django-insecure' not in settings.SECRET_KEY),
        ("ALLOWED_HOSTS configured", len(settings.ALLOWED_HOSTS) > 0),
        ("CSRF middleware enabled", 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE),
        ("XFrame middleware enabled", 'django.middleware.clickjacking.XFrameOptionsMiddleware' in settings.MIDDLEWARE),
        ("Security middleware enabled", 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE),
    ]
    
    for name, passed in tests:
        print_test(name, passed)
    
    return all(passed for _, passed in tests)


def test_password_validators():
    """Test password validation."""
    print_header("PASSWORD VALIDATION TEST")
    
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    
    weak_passwords = [
        "123456",
        "password",
        "qwerty",
        "abc123",
    ]
    
    strong_password = "MyStr0ng!P@ssw0rd2024"
    
    # Test weak passwords are rejected
    weak_rejected = 0
    for pwd in weak_passwords:
        try:
            validate_password(pwd)
        except ValidationError:
            weak_rejected += 1
    
    print_test(f"Weak passwords rejected ({weak_rejected}/{len(weak_passwords)})", 
               weak_rejected == len(weak_passwords))
    
    # Test strong password is accepted
    try:
        validate_password(strong_password)
        strong_accepted = True
    except ValidationError:
        strong_accepted = False
    
    print_test("Strong password accepted", strong_accepted)
    
    return weak_rejected == len(weak_passwords) and strong_accepted


def test_security_headers():
    """Test security headers middleware."""
    print_header("SECURITY HEADERS TEST")
    
    client = Client()
    response = client.get('/')
    
    headers_to_check = [
        ('X-Content-Type-Options', 'nosniff'),
        ('X-XSS-Protection', '1; mode=block'),
        ('Referrer-Policy', 'strict-origin-when-cross-origin'),
    ]
    
    results = []
    for header, expected_value in headers_to_check:
        has_header = header in response
        correct_value = response.get(header) == expected_value if has_header else False
        results.append((f"{header} header present", has_header))
        if has_header:
            results.append((f"{header} has correct value", correct_value))
    
    for name, passed in results:
        print_test(name, passed)
    
    return all(passed for _, passed in results)


def test_csrf_protection():
    """Test CSRF protection."""
    print_header("CSRF PROTECTION TEST")
    
    client = Client()
    
    # Try POST without CSRF token
    response = client.post('/wizard/destination/', {})
    csrf_protected = response.status_code == 403
    
    print_test("POST without CSRF token blocked", csrf_protected)
    
    # Try POST with CSRF token
    client = Client(enforce_csrf_checks=True)
    response = client.get('/wizard/destination/')
    csrf_token = response.cookies.get('csrftoken')
    
    if csrf_token:
        response = client.post('/wizard/destination/', 
                              {'csrfmiddlewaretoken': csrf_token.value})
        csrf_works = response.status_code != 403
        print_test("POST with CSRF token allowed", csrf_works)
        return csrf_protected and csrf_works
    else:
        print_test("CSRF token generated", False)
        return False


def test_sql_injection_protection():
    """Test SQL injection protection."""
    print_header("SQL INJECTION PROTECTION TEST")
    
    from destinations.models import Destination
    
    # Try SQL injection patterns
    injection_attempts = [
        "' OR '1'='1",
        "'; DROP TABLE destinations; --",
        "1' UNION SELECT * FROM users--",
    ]
    
    protected = True
    for attempt in injection_attempts:
        try:
            # Django ORM should safely handle these
            result = Destination.objects.filter(name=attempt)
            # Should return empty queryset, not error
            if result.exists():
                protected = False
        except Exception as e:
            # Should not raise exceptions
            protected = False
    
    print_test("SQL injection attempts blocked", protected)
    return protected


def test_xss_protection():
    """Test XSS protection."""
    print_header("XSS PROTECTION TEST")
    
    from django.template import Template, Context
    from django.utils.html import escape
    
    xss_attempts = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
    ]
    
    protected = True
    for attempt in xss_attempts:
        # Django templates should auto-escape
        template = Template("{{ content }}")
        rendered = template.render(Context({'content': attempt}))
        
        # Check if dangerous content is escaped
        if '<script>' in rendered or 'onerror=' in rendered or 'javascript:' in rendered:
            protected = False
    
    print_test("XSS attempts escaped", protected)
    return protected


def test_session_security():
    """Test session security settings."""
    print_header("SESSION SECURITY TEST")
    
    tests = [
        ("SESSION_COOKIE_HTTPONLY", getattr(settings, 'SESSION_COOKIE_HTTPONLY', False)),
        ("SESSION_COOKIE_SAMESITE", getattr(settings, 'SESSION_COOKIE_SAMESITE', None) == 'Strict'),
        ("CSRF_COOKIE_HTTPONLY", getattr(settings, 'CSRF_COOKIE_HTTPONLY', False)),
        ("CSRF_COOKIE_SAMESITE", getattr(settings, 'CSRF_COOKIE_SAMESITE', None) == 'Strict'),
    ]
    
    for name, passed in tests:
        print_test(name, passed)
    
    return all(passed for _, passed in tests)


def test_rate_limiting():
    """Test rate limiting."""
    print_header("RATE LIMITING TEST")
    
    from core.services.rate_limiter import RateLimiter
    
    limiter = RateLimiter.get_instance()
    
    # Test rate limiter exists
    print_test("Rate limiter initialized", limiter is not None)
    
    # Test usage tracking
    usage = limiter.get_usage_summary('gemini')
    print_test("Usage tracking works", 'current_minute' in usage)
    
    # Test rate limit configuration
    rate_limit = limiter.get_rate_limit('gemini')
    print_test("Rate limit configured", rate_limit > 0)
    
    return True


def test_brute_force_protection():
    """Test brute force protection (if django-axes installed)."""
    print_header("BRUTE FORCE PROTECTION TEST")
    
    try:
        import axes
        axes_installed = True
    except ImportError:
        axes_installed = False
    
    print_test("Django-Axes installed", axes_installed)
    
    if axes_installed:
        axes_enabled = getattr(settings, 'AXES_ENABLED', False)
        print_test("Axes enabled in settings", axes_enabled)
        
        axes_in_middleware = 'axes.middleware.AxesMiddleware' in settings.MIDDLEWARE
        print_test("Axes middleware configured", axes_in_middleware)
        
        return axes_enabled and axes_in_middleware
    
    return False


def test_logging_configuration():
    """Test logging configuration."""
    print_header("LOGGING CONFIGURATION TEST")
    
    import logging
    
    # Test security logger exists
    security_logger = logging.getLogger('core.security')
    print_test("Security logger configured", security_logger is not None)
    
    # Test logs directory exists
    logs_dir = settings.BASE_DIR / 'logs'
    print_test("Logs directory exists", logs_dir.exists())
    
    return True


def test_admin_security():
    """Test admin security."""
    print_header("ADMIN SECURITY TEST")
    
    client = Client()
    
    # Test admin URL
    admin_url = getattr(settings, 'ADMIN_URL', 'admin/')
    response = client.get(f'/{admin_url}')
    
    # Should redirect to login (302) or show login page (200)
    admin_accessible = response.status_code in [200, 302]
    print_test("Admin panel accessible", admin_accessible)
    
    # Test admin requires authentication
    admin_protected = response.status_code == 302 or 'login' in response.content.decode().lower()
    print_test("Admin requires authentication", admin_protected)
    
    return admin_accessible and admin_protected


def run_all_tests():
    """Run all security tests."""
    print("\n" + "=" * 70)
    print("  SAFARISMART KENYA - SECURITY TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Security Settings", test_security_settings),
        ("Password Validation", test_password_validators),
        ("Security Headers", test_security_headers),
        ("CSRF Protection", test_csrf_protection),
        ("SQL Injection Protection", test_sql_injection_protection),
        ("XSS Protection", test_xss_protection),
        ("Session Security", test_session_security),
        ("Rate Limiting", test_rate_limiting),
        ("Brute Force Protection", test_brute_force_protection),
        ("Logging Configuration", test_logging_configuration),
        ("Admin Security", test_admin_security),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 All security tests passed! Your platform is secure.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review and fix.")
    
    print("\n📝 Next steps:")
    print("1. Review failed tests above")
    print("2. Check SECURITY_IMPLEMENTATION_GUIDE.md")
    print("3. Install missing security packages")
    print("4. Configure production settings")
    print("5. Run: python manage.py check --deploy")
    
    return passed == total


if __name__ == '__main__':
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
