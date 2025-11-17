"""
Quick test script for API rate limiting system.

Run with: python test_rate_limiter.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from core.services.rate_limiter import RateLimiter
from core.models_api_tracking import APIUsageLog, APIUsageStats


def test_rate_limiter():
    """Test rate limiter functionality."""
    print("=" * 60)
    print("API RATE LIMITER TEST")
    print("=" * 60)
    
    limiter = RateLimiter.get_instance()
    
    # Test 1: Get usage summary
    print("\n1. Current Usage Summary:")
    print("-" * 60)
    summary = limiter.get_usage_summary('gemini')
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test 2: Check rate limit status
    print("\n2. Rate Limit Status:")
    print("-" * 60)
    is_limited = limiter.is_rate_limited('gemini')
    print(f"  Is rate limited: {is_limited}")
    print(f"  Rate limit: {limiter.get_rate_limit('gemini')} requests/minute")
    print(f"  Current usage: {limiter.get_current_usage('gemini')} requests")
    
    # Test 3: Simulate API call
    print("\n3. Simulating API Call:")
    print("-" * 60)
    
    def mock_api_call():
        """Mock API function."""
        import time
        time.sleep(0.1)  # Simulate API delay
        return "Mock response"
    
    try:
        result = limiter.execute('gemini', mock_api_call)
        print(f"  Result: {result}")
        print("  ✓ API call successful")
    except Exception as e:
        print(f"  ✗ API call failed: {e}")
    
    # Test 4: Check database logs
    print("\n4. Recent API Logs:")
    print("-" * 60)
    recent_logs = APIUsageLog.objects.all()[:5]
    if recent_logs:
        for log in recent_logs:
            print(f"  {log.request_time.strftime('%H:%M:%S')} - "
                  f"{log.api_name} - {log.status} - "
                  f"{log.response_time:.2f}s" if log.response_time else "N/A")
    else:
        print("  No logs yet")
    
    # Test 5: Today's statistics
    print("\n5. Today's Statistics:")
    print("-" * 60)
    from django.utils import timezone
    today = timezone.now().date()
    today_logs = APIUsageLog.objects.filter(request_time__date=today)
    
    print(f"  Total calls: {today_logs.count()}")
    print(f"  Successful: {today_logs.filter(status='success').count()}")
    print(f"  Failed: {today_logs.filter(status='failure').count()}")
    print(f"  Rate limited: {today_logs.filter(status='rate_limited').count()}")
    
    total_cost = sum(log.estimated_cost for log in today_logs)
    print(f"  Total cost: ${total_cost:.4f} (KSh {total_cost * 150:.2f})")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Visit Django admin at http://localhost:8000/admin/")
    print("2. Check 'API Usage Logs' for real-time monitoring")
    print("3. Check 'API Usage Statistics' for aggregated data")
    print("4. Adjust rate limits in 'System Configuration'")


if __name__ == '__main__':
    test_rate_limiter()
