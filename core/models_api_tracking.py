"""
Module: core/models_api_tracking.py
Purpose: API usage tracking and analytics models

This module tracks API usage for cost control, quota management,
and usage analytics.

Classes:
    APIUsageLog: Individual API call tracking
    APIUsageStats: Aggregated usage statistics
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime, timedelta


class APIUsageLog(models.Model):
    """
    Tracks individual API calls for monitoring and analytics.
    
    Records every API call with timing, cost, and outcome data.
    Used for real-time monitoring and historical analysis.
    
    Attributes:
        api_name (str): API service name (gemini, weather, etc.)
        endpoint (str): Specific endpoint called
        request_time (datetime): When request was made
        response_time (float): Response time in seconds
        status (str): Success, failure, rate_limited, queued
        tokens_used (int): Tokens consumed (for AI APIs)
        estimated_cost (Decimal): Estimated cost in USD
        error_message (str): Error details if failed
        user_id (int): User who triggered the call (optional)
        ip_address (str): Request IP address
    """
    
    API_CHOICES = [
        ('gemini', 'Gemini AI'),
        ('weather', 'Weather API'),
        ('maps', 'Maps API'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('rate_limited', 'Rate Limited'),
        ('queued', 'Queued'),
        ('timeout', 'Timeout'),
    ]
    
    api_name = models.CharField(
        max_length=50,
        choices=API_CHOICES,
        db_index=True,
        help_text="API service name"
    )
    endpoint = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specific endpoint or method called"
    )
    request_time = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the request was made"
    )
    response_time = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Response time in seconds"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        db_index=True,
        help_text="Request outcome"
    )
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Tokens consumed (for AI APIs)"
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=Decimal('0.000000'),
        validators=[MinValueValidator(0)],
        help_text="Estimated cost in USD"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error details if request failed"
    )
    user_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="User who triggered the call"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Request IP address"
    )
    
    # Additional metadata
    request_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Request parameters (sanitized)"
    )
    response_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Response summary (sanitized)"
    )
    
    class Meta:
        ordering = ['-request_time']
        verbose_name = "API Usage Log"
        verbose_name_plural = "API Usage Logs"
        indexes = [
            models.Index(fields=['api_name', 'request_time']),
            models.Index(fields=['status', 'request_time']),
            models.Index(fields=['request_time']),
        ]
        
    def __str__(self) -> str:
        return f"{self.api_name} - {self.status} - {self.request_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
    @property
    def is_successful(self) -> bool:
        """Check if request was successful."""
        return self.status == 'success'
        
    @property
    def cost_in_ksh(self) -> Decimal:
        """Convert cost to KSh (approximate rate: 1 USD = 150 KSh)."""
        return self.estimated_cost * Decimal('150')


class APIUsageStats(models.Model):
    """
    Aggregated API usage statistics by time period.
    
    Pre-calculated statistics for fast dashboard queries.
    Updated periodically by background task.
    
    Attributes:
        api_name (str): API service name
        period_type (str): Hour, day, month
        period_start (datetime): Period start time
        total_calls (int): Total API calls
        successful_calls (int): Successful calls
        failed_calls (int): Failed calls
        rate_limited_calls (int): Rate limited calls
        total_tokens (int): Total tokens used
        total_cost (Decimal): Total cost in USD
        avg_response_time (float): Average response time
    """
    
    PERIOD_CHOICES = [
        ('hour', 'Hourly'),
        ('day', 'Daily'),
        ('month', 'Monthly'),
    ]
    
    api_name = models.CharField(
        max_length=50,
        db_index=True,
        help_text="API service name"
    )
    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        db_index=True,
        help_text="Aggregation period"
    )
    period_start = models.DateTimeField(
        db_index=True,
        help_text="Period start time"
    )
    
    # Call counts
    total_calls = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total API calls in period"
    )
    successful_calls = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Successful calls"
    )
    failed_calls = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Failed calls"
    )
    rate_limited_calls = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Rate limited calls"
    )
    queued_calls = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Queued calls"
    )
    
    # Usage metrics
    total_tokens = models.BigIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total tokens consumed"
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0.000000'),
        validators=[MinValueValidator(0)],
        help_text="Total cost in USD"
    )
    avg_response_time = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Average response time in seconds"
    )
    
    # Metadata
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )
    
    class Meta:
        ordering = ['-period_start']
        verbose_name = "API Usage Statistics"
        verbose_name_plural = "API Usage Statistics"
        unique_together = [['api_name', 'period_type', 'period_start']]
        indexes = [
            models.Index(fields=['api_name', 'period_type', 'period_start']),
            models.Index(fields=['period_start']),
        ]
        
    def __str__(self) -> str:
        return f"{self.api_name} - {self.period_type} - {self.period_start.strftime('%Y-%m-%d %H:%M')}"
        
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
        
    @property
    def cost_in_ksh(self) -> Decimal:
        """Convert cost to KSh."""
        return self.total_cost * Decimal('150')
        
    @classmethod
    def get_current_minute_usage(cls, api_name: str) -> int:
        """
        Get API calls in current minute.
        
        Args:
            api_name (str): API service name
            
        Returns:
            int: Number of calls in current minute
        """
        now = timezone.now()
        minute_start = now.replace(second=0, microsecond=0)
        
        return APIUsageLog.objects.filter(
            api_name=api_name,
            request_time__gte=minute_start,
            status='success'
        ).count()
        
    @classmethod
    def get_today_usage(cls, api_name: str) -> dict:
        """
        Get today's usage summary.
        
        Args:
            api_name (str): API service name
            
        Returns:
            dict: Usage summary
        """
        today = timezone.now().date()
        
        logs = APIUsageLog.objects.filter(
            api_name=api_name,
            request_time__date=today
        )
        
        return {
            'total_calls': logs.count(),
            'successful': logs.filter(status='success').count(),
            'failed': logs.filter(status='failure').count(),
            'rate_limited': logs.filter(status='rate_limited').count(),
            'total_cost': sum(log.estimated_cost for log in logs),
        }
