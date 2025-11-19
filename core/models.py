from django.db import models
from django.contrib.auth.models import User
from destinations.models import Destination
import uuid


class WizardSession(models.Model):
    """Stores wizard progress for users (logged in or anonymous)"""
    session_key = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Step 1: Destinations
    selected_destinations = models.ManyToManyField(Destination, blank=True)
    
    # Step 2: Duration
    duration_days = models.IntegerField(null=True, blank=True)
    travel_start_date = models.DateField(null=True, blank=True)
    travel_end_date = models.DateField(null=True, blank=True)
    
    # Step 3: Travel Group
    adults_count = models.IntegerField(default=2)
    children_count = models.IntegerField(default=0)
    travel_type = models.CharField(max_length=20, null=True, blank=True)  # solo, family, couple, friends
    
    # Step 4: Budget
    budget_amount = models.IntegerField(null=True, blank=True, help_text="Total budget in KSh")
    budget_category = models.CharField(max_length=20, null=True, blank=True)  # budget, mid-range, luxury
    
    # Step 5: Interests
    interests = models.JSONField(default=list, blank=True)  # ['wildlife', 'culture', 'food', etc.]
    
    # Meta
    current_step = models.IntegerField(default=1)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wizard Session {self.session_key} - Step {self.current_step}"


class Itinerary(models.Model):
    """Generated trip itinerary"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    share_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Trip details
    title = models.CharField(max_length=200)
    destinations = models.ManyToManyField(Destination)
    duration_days = models.IntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Group details
    adults_count = models.IntegerField(default=2)
    children_count = models.IntegerField(default=0)
    travel_type = models.CharField(max_length=20)
    
    # Budget
    total_budget = models.IntegerField(help_text="Total budget in KSh")
    budget_category = models.CharField(max_length=20)
    
    # AI Generated content
    itinerary_data = models.JSONField(help_text="Full day-by-day itinerary from Gemini")
    cost_breakdown = models.JSONField(help_text="Detailed cost breakdown")
    
    # Meta
    is_saved = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Itineraries'
    
    def __str__(self):
        return f"{self.title} - {self.duration_days} days"
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


# Import configuration models
from .models_config import (
    TravelType,
    BudgetCategory,
    InterestCategory,
    BudgetEstimate,
    SystemConfiguration
)

# Import API tracking models
from .models_api_tracking import (
    APIUsageLog,
    APIUsageStats
)

# Import security models
from .models_security import (
    SecuritySettings,
    SecurityEvent
)

# Import static pages models
from .models_pages import StaticPage, ContactInfo

__all__ = [
    'WizardSession',
    'Itinerary',
    'TravelType',
    'BudgetCategory',
    'InterestCategory',
    'BudgetEstimate',
    'SystemConfiguration',
    'APIUsageLog',
    'APIUsageStats',
    'SecuritySettings',
    'SecurityEvent',
]
