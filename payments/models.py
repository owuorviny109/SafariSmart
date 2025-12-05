from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

class PaymentConfiguration(models.Model):
    """
    Singleton model to control payment settings from Admin.
    Allows toggling features and setting amounts without code changes.
    """
    # Singleton ID
    singleton_id = models.IntegerField(default=1, unique=True, editable=False)
    
    # Feature Toggles
    enable_mpesa = models.BooleanField(
        default=True,
        help_text="Master switch for M-Pesa payments"
    )
    enable_sponsorship = models.BooleanField(
        default=True,
        help_text="Enable 'Buy us a Coffee' / Sponsorship feature"
    )
    enable_subscriptions = models.BooleanField(
        default=False,
        help_text="Enable recurring subscription plans (Future use)"
    )
    enable_flutterwave = models.BooleanField(
        default=True,
        help_text="Enable Card/Global payments via Flutterwave"
    )
    
    # Environment Configuration
    MPESA_ENV_CHOICES = [
        ('sandbox', 'Sandbox (Test)'),
        ('production', 'Production (Live)'),
    ]
    mpesa_environment = models.CharField(
        max_length=20,
        choices=MPESA_ENV_CHOICES,
        default='sandbox',
        help_text="Switch between Test and Live modes"
    )
    
    # Transaction Limits
    min_transaction_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=10.00,
        help_text="Minimum allowed transaction amount in KSh"
    )
    
    # Sponsorship Options (JSON)
    # Stores the preset buttons shown on the UI, e.g., [100, 500, 1000]
    sponsorship_options = models.JSONField(
        default=list,
        help_text="List of preset amounts for sponsorship buttons (e.g., [100, 500, 1000])"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Payment Configuration"
        verbose_name_plural = "Payment Configuration"

    def __str__(self):
        return "Payment System Configuration"

    def save(self, *args, **kwargs):
        self.singleton_id = 1
        # Set default options if empty
        if not self.sponsorship_options:
            self.sponsorship_options = [1000, 2500, 5000, 10000]
        cache.delete('payment_config') # Invalidate cache
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        config = cache.get('payment_config')
        if not config:
            config, created = cls.objects.get_or_create(singleton_id=1)
            cache.set('payment_config', config, 300) # Cache for 5 mins
        return config


class PaymentTransaction(models.Model):
    """
    Records every M-Pesa transaction attempt and result.
    """
    TRANSACTION_TYPES = [
        ('sponsorship', 'Sponsorship/Donation'),
        ('itinerary', 'Itinerary Purchase'),
        ('subscription', 'Subscription'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Identification
    transaction_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="M-Pesa Receipt Number (e.g., QKH1...)"
    )
    checkout_request_id = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Unique ID for the STK Push request"
    )
    merchant_request_id = models.CharField(
        max_length=100,
        null=True, 
        blank=True
    )
    
    # Provider Info
    PROVIDER_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('flutterwave', 'Flutterwave (Card)'),
    ]
    payment_provider = models.CharField(
        max_length=20, 
        choices=PROVIDER_CHOICES, 
        default='mpesa'
    )
    flutterwave_ref = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Flutterwave Transaction Reference (tx_ref)"
    )
    
    # Transaction Details
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transactions'
    )
    phone_number = models.CharField(max_length=15, help_text="Format: 2547...")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(
        max_length=100, 
        help_text="Internal reference (e.g., Order ID or 'Sponsorship')"
    )
    description = models.CharField(max_length=255)
    
    # Status & Result
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['checkout_request_id']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transaction_id or 'PENDING'} - {self.amount} ({self.status})"
