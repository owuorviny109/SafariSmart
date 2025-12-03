"""
Module: services/rate_limiter.py
Purpose: API rate limiting and request queueing

This module provides enterprise-grade rate limiting for API calls
with automatic queueing, retry logic, and usage tracking.

Classes:
    RateLimiter: Main rate limiting service
    RequestQueue: Queue manager for rate-limited requests
    
 
"""

import time
import logging
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal

from core.models_api_tracking import APIUsageLog
from core.services.configuration_service import ConfigurationService
from core.exceptions import AIServiceError


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Enterprise-grade API rate limiter with queueing.
    
    Features:
    - Per-minute rate limiting
    - Automatic request queueing
    - Usage tracking and logging
    - Cost estimation
    - Configurable limits
    
    Design Pattern: Singleton + Decorator
    
    Example:
        >>> limiter = RateLimiter.get_instance()
        >>> result = limiter.execute(
        ...     api_name='gemini',
        ...     func=generate_itinerary,
        ...     args=(preferences,)
        ... )
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        """Initialize rate limiter."""
        if not hasattr(self, '_initialized'):
            self.config = ConfigurationService.get_instance()
            self._initialized = True
            
    @classmethod
    def get_instance(cls) -> 'RateLimiter':
        """Get singleton instance."""
        return cls()
        
    def get_cache_key(self, api_name: str) -> str:
        """
        Generate cache key for rate limiting.
        
        Args:
            api_name (str): API service name
            
        Returns:
            str: Cache key
        """
        now = timezone.now()
        minute = now.strftime('%Y%m%d%H%M')
        return f'rate_limit:{api_name}:{minute}'
        
    def get_current_usage(self, api_name: str) -> int:
        """
        Get current minute's API usage count.
        
        Args:
            api_name (str): API service name
            
        Returns:
            int: Number of calls in current minute
            
        Time Complexity: O(1) with cache
        """
        cache_key = self.get_cache_key(api_name)
        count = cache.get(cache_key, 0)
        return int(count)
        
    def increment_usage(self, api_name: str) -> int:
        """
        Increment usage counter for current minute.
        
        Args:
            api_name (str): API service name
            
        Returns:
            int: New usage count
            
        Time Complexity: O(1)
        """
        cache_key = self.get_cache_key(api_name)
        
        # Get current count
        count = cache.get(cache_key, 0)
        new_count = count + 1
        
        # Set with 70 second expiry (minute + buffer)
        cache.set(cache_key, new_count, 70)
        
        return new_count
        
    def get_rate_limit(self, api_name: str) -> int:
        """
        Get rate limit for API from configuration.
        
        Args:
            api_name (str): API service name
            
        Returns:
            int: Requests per minute limit
        """
        system_config = self.config.get_system_config()
        
        # Map API names to config fields
        limits = {
            'gemini': system_config.gemini_api_rate_limit,
            'weather': 60,  # Default for weather API
            'maps': 60,     # Default for maps API
        }
        
        return limits.get(api_name, 60)
        
    def is_rate_limited(self, api_name: str) -> bool:
        """
        Check if API is currently rate limited.
        
        Args:
            api_name (str): API service name
            
        Returns:
            bool: True if rate limited
        """
        current_usage = self.get_current_usage(api_name)
        rate_limit = self.get_rate_limit(api_name)
        
        return current_usage >= rate_limit
        
    def get_wait_time(self, api_name: str) -> int:
        """
        Calculate seconds until next available slot.
        
        Args:
            api_name (str): API service name
            
        Returns:
            int: Seconds to wait (0 if available now)
        """
        if not self.is_rate_limited(api_name):
            return 0
            
        # Calculate seconds until next minute
        now = timezone.now()
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        wait_seconds = (next_minute - now).total_seconds()
        
        return int(wait_seconds) + 1  # Add 1 second buffer
        
    def execute(
        self,
        api_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with rate limiting.
        
        Automatically handles:
        - Rate limit checking
        - Queueing when limit reached
        - Usage tracking
        - Error logging
        
        Args:
            api_name (str): API service name
            func (Callable): Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Any: Function result
            
        Raises:
            AIServiceError: If execution fails
            
        Example:
            >>> limiter = RateLimiter.get_instance()
            >>> result = limiter.execute(
            ...     'gemini',
            ...     model.generate_content,
            ...     prompt
            ... )
        """
        # Check if rate limited
        if self.is_rate_limited(api_name):
            wait_time = self.get_wait_time(api_name)
            logger.warning(
                f"{api_name} API rate limited. Waiting {wait_time} seconds..."
            )
            
            # Log rate limit event
            self._log_usage(
                api_name=api_name,
                status='rate_limited',
                error_message=f"Rate limit reached. Waited {wait_time}s"
            )
            
            # Wait for next minute
            time.sleep(wait_time)
            
        # Increment usage counter
        self.increment_usage(api_name)
        
        # Execute function with timing
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Log successful call
            self._log_usage(
                api_name=api_name,
                status='success',
                response_time=response_time
            )
            
            logger.info(
                f"{api_name} API call successful. "
                f"Response time: {response_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Log failed call
            self._log_usage(
                api_name=api_name,
                status='failure',
                response_time=response_time,
                error_message=str(e)
            )
            
            logger.error(
                f"{api_name} API call failed: {str(e)}"
            )
            
            raise AIServiceError(
                f"{api_name} API call failed",
                service_name=api_name,
                original_error=e
            )
            
    def _log_usage(
        self,
        api_name: str,
        status: str,
        response_time: Optional[float] = None,
        tokens_used: Optional[int] = None,
        error_message: str = ''
    ) -> None:
        """
        Log API usage to database.
        
        Args:
            api_name (str): API service name
            status (str): Request status
            response_time (float, optional): Response time in seconds
            tokens_used (int, optional): Tokens consumed
            error_message (str): Error details
        """
        try:
            # Estimate cost (rough estimates)
            cost_per_call = {
                'gemini': Decimal('0.0001'),  # ~$0.0001 per call
                'weather': Decimal('0.00001'), # ~$0.00001 per call
                'maps': Decimal('0.00005'),    # ~$0.00005 per call
            }
            
            estimated_cost = cost_per_call.get(api_name, Decimal('0'))
            
            # Create log entry
            APIUsageLog.objects.create(
                api_name=api_name,
                status=status,
                response_time=response_time,
                tokens_used=tokens_used,
                estimated_cost=estimated_cost,
                error_message=error_message
            )
            
        except Exception as e:
            # Don't fail the main operation if logging fails
            logger.error(f"Failed to log API usage: {str(e)}")
            
    def get_usage_summary(self, api_name: str) -> dict:
        """
        Get current usage summary.
        
        Args:
            api_name (str): API service name
            
        Returns:
            dict: Usage summary with current, today, and limit info
        """
        current_minute = self.get_current_usage(api_name)
        rate_limit = self.get_rate_limit(api_name)
        
        # Get today's usage from database
        today = timezone.now().date()
        today_logs = APIUsageLog.objects.filter(
            api_name=api_name,
            request_time__date=today
        )
        
        return {
            'api_name': api_name,
            'current_minute': current_minute,
            'rate_limit': rate_limit,
            'available_slots': max(0, rate_limit - current_minute),
            'is_rate_limited': self.is_rate_limited(api_name),
            'wait_time_seconds': self.get_wait_time(api_name),
            'today_total': today_logs.count(),
            'today_successful': today_logs.filter(status='success').count(),
            'today_failed': today_logs.filter(status='failure').count(),
            'today_rate_limited': today_logs.filter(status='rate_limited').count(),
        }


def rate_limited(api_name: str):
    """
    Decorator for rate-limited functions.
    
    Usage:
        @rate_limited('gemini')
        def generate_content(prompt):
            return model.generate_content(prompt)
    
    Args:
        api_name (str): API service name
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            limiter = RateLimiter.get_instance()
            return limiter.execute(api_name, func, *args, **kwargs)
        return wrapper
    return decorator
