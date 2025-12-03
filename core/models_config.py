"""
Module: core/models_config.py
Purpose: Configuration models for admin-manageable settings

This module contains models for application configuration that should
be managed through Django admin rather than hardcoded in code.

Classes:
    TravelType: Available travel types (solo, family, etc.)
    BudgetCategory: Budget tiers with cost estimates
    InterestCategory: User interest categories
    BudgetEstimate: Daily budget breakdowns by category
    SystemConfiguration: Global system settings
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class TravelType(models.Model):
    """
    Travel type configuration (solo, family, couple, friends).
    
    Allows admin to add/remove/modify travel types without code changes.
    
    Attributes:
        code (str): Unique identifier for travel type
        name (str): Display name
        description (str): Detailed description
        icon (str): Icon class or emoji
        is_active (bool): Whether this type is available
        sort_order (int): Display order
        
    Example:
        >>> travel_type = TravelType.objects.get(code='family')
        >>> print(travel_type.name)
        'Family Trip'
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier (e.g., 'solo', 'family')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Family Trip')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of this travel type"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or emoji (e.g., 'bi-people', '👨‍👩‍👧‍👦')"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this travel type is available for selection"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Travel Type"
        verbose_name_plural = "Travel Types"
        
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
        
    def clean(self):
        """Validate model data."""
        if self.code:
            self.code = self.code.lower().strip()


class BudgetCategory(models.Model):
    """
    Budget category configuration (budget, mid-range, luxury).
    
    Allows admin to configure budget tiers and their characteristics.
    
    Attributes:
        code (str): Unique identifier
        name (str): Display name
        description (str): Description
        min_budget_per_day (int): Minimum daily budget in KSh
        max_budget_per_day (int): Maximum daily budget in KSh
        is_active (bool): Whether available
        sort_order (int): Display order
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier (e.g., 'budget', 'mid-range', 'luxury')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Budget-Friendly')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this budget tier includes"
    )
    min_budget_per_day = models.IntegerField(
        validators=[MinValueValidator(1000)],
        help_text="Minimum daily budget in KSh"
    )
    max_budget_per_day = models.IntegerField(
        validators=[MinValueValidator(1000)],
        help_text="Maximum daily budget in KSh"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or emoji"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this budget category is available"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'min_budget_per_day']
        verbose_name = "Budget Category"
        verbose_name_plural = "Budget Categories"
        
    def __str__(self) -> str:
        return f"{self.name} (KSh {self.min_budget_per_day:,} - {self.max_budget_per_day:,})"
        
    def clean(self):
        """Validate budget ranges."""
        if self.code:
            self.code = self.code.lower().strip()
            
        if self.max_budget_per_day <= self.min_budget_per_day:
            raise ValidationError(
                "Maximum budget must be greater than minimum budget"
            )


class InterestCategory(models.Model):
    """
    User interest categories (wildlife, culture, food, etc.).
    
    Allows admin to add/remove interest categories without code changes.
    
    Attributes:
        code (str): Unique identifier
        name (str): Display name
        description (str): Description
        icon (str): Icon class or emoji
        is_active (bool): Whether available
        sort_order (int): Display order
    """
    
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier (e.g., 'wildlife', 'culture')"
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Wildlife & Safari')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this interest category"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class or emoji (e.g., 'bi-binoculars', '🦁')"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this interest is available for selection"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Interest Category"
        verbose_name_plural = "Interest Categories"
        
    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
        
    def clean(self):
        """Validate model data."""
        if self.code:
            self.code = self.code.lower().strip()


class BudgetEstimate(models.Model):
    """
    Daily budget breakdown estimates by category.
    
    Stores estimated costs for accommodation, activities, meals, and
    transport for each budget category. Admin-configurable.
    
    Attributes:
        budget_category (ForeignKey): Related budget category
        accommodation_min (int): Min accommodation cost per day
        accommodation_max (int): Max accommodation cost per day
        activities_min (int): Min activities cost per day
        activities_max (int): Max activities cost per day
        meals_min (int): Min meals cost per day
        meals_max (int): Max meals cost per day
        transport_min (int): Min transport cost per day
        transport_max (int): Max transport cost per day
    """
    
    budget_category = models.OneToOneField(
        BudgetCategory,
        on_delete=models.CASCADE,
        related_name='estimate',
        help_text="Budget category for these estimates"
    )
    
    # Accommodation estimates
    accommodation_min = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum accommodation cost per day (KSh)"
    )
    accommodation_max = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum accommodation cost per day (KSh)"
    )
    
    # Activities estimates
    activities_min = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum activities cost per day (KSh)"
    )
    activities_max = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum activities cost per day (KSh)"
    )
    
    # Meals estimates
    meals_min = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum meals cost per day (KSh)"
    )
    meals_max = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum meals cost per day (KSh)"
    )
    
    # Transport estimates
    transport_min = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Minimum transport cost per day (KSh)"
    )
    transport_max = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum transport cost per day (KSh)"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about these estimates"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Budget Estimate"
        verbose_name_plural = "Budget Estimates"
        
    def __str__(self) -> str:
        return f"Estimates for {self.budget_category.name}"
        
    def clean(self):
        """Validate estimate ranges."""
        fields = [
            ('accommodation', self.accommodation_min, self.accommodation_max),
            ('activities', self.activities_min, self.activities_max),
            ('meals', self.meals_min, self.meals_max),
            ('transport', self.transport_min, self.transport_max),
        ]
        
        for field_name, min_val, max_val in fields:
            if max_val < min_val:
                raise ValidationError(
                    f"{field_name.capitalize()} maximum must be >= minimum"
                )
                
    def get_total_min(self) -> int:
        """Calculate minimum total daily cost."""
        return (
            self.accommodation_min +
            self.activities_min +
            self.meals_min +
            self.transport_min
        )
        
    def get_total_max(self) -> int:
        """Calculate maximum total daily cost."""
        return (
            self.accommodation_max +
            self.activities_max +
            self.meals_max +
            self.transport_max
        )


class SystemConfiguration(models.Model):
    """
    Global system configuration settings.
    
    Singleton model for system-wide settings that should be
    admin-configurable rather than hardcoded.
    
    Attributes:
        min_trip_duration (int): Minimum trip duration in days
        max_trip_duration (int): Maximum trip duration in days
        min_budget (int): Minimum total budget in KSh
        max_budget (int): Maximum total budget in KSh
        max_travelers (int): Maximum number of travelers
        max_destinations (int): Maximum destinations per trip
        max_interests (int): Maximum interests per user
    """
    
    # Trip duration constraints
    min_trip_duration = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum trip duration in days"
    )
    max_trip_duration = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Maximum trip duration in days"
    )
    
    # Budget constraints
    min_budget = models.IntegerField(
        default=10000,
        validators=[MinValueValidator(1000)],
        help_text="Minimum total budget in KSh"
    )
    max_budget = models.IntegerField(
        default=500000,
        validators=[MinValueValidator(1000)],
        help_text="Maximum total budget in KSh"
    )
    
    # Traveler constraints
    min_adults = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum number of adults"
    )
    max_adults = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        help_text="Maximum number of adults"
    )
    max_children = models.IntegerField(
        default=20,
        validators=[MinValueValidator(0)],
        help_text="Maximum number of children"
    )
    max_total_travelers = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Maximum total travelers (adults + children)"
    )
    
    # Selection constraints
    max_destinations = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum destinations per trip"
    )
    max_interests = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum interests per user"
    )
    
    # Feature flags
    enable_ai_generation = models.BooleanField(
        default=True,
        help_text="Enable AI-powered itinerary generation"
    )
    enable_weather_forecasts = models.BooleanField(
        default=True,
        help_text="Enable weather forecast integration"
    )
    enable_custom_destinations = models.BooleanField(
        default=True,
        help_text="Allow users to add custom destinations"
    )
    enable_user_registration = models.BooleanField(
        default=True,
        help_text="Allow new user registrations"
    )
    enable_itinerary_sharing = models.BooleanField(
        default=True,
        help_text="Allow users to share itineraries"
    )
    enable_itinerary_saving = models.BooleanField(
        default=True,
        help_text="Allow users to save itineraries"
    )
    
    # System maintenance
    maintenance_mode = models.BooleanField(
        default=False,
        help_text="Enable maintenance mode (site unavailable to users)"
    )
    maintenance_message = models.TextField(
        blank=True,
        default="We're currently performing maintenance. Please check back soon!",
        help_text="Message to display during maintenance"
    )
    
    # Rate limiting
    enable_rate_limiting = models.BooleanField(
        default=True,
        help_text="Enable rate limiting for API requests"
    )
    max_itineraries_per_day = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum itineraries a user can generate per day"
    )
    max_itineraries_per_hour = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text="Maximum itineraries a user can generate per hour"
    )
    
    # Analytics and tracking
    enable_analytics = models.BooleanField(
        default=True,
        help_text="Enable Google Analytics tracking"
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Google Analytics tracking ID (e.g., G-XXXXXXXXXX)"
    )
    enable_error_reporting = models.BooleanField(
        default=True,
        help_text="Enable automatic error reporting"
    )
    
    # SEO settings
    site_name = models.CharField(
        max_length=100,
        default="SafariSmart Kenya",
        help_text="Site name for SEO"
    )
    site_tagline = models.CharField(
        max_length=200,
        default="AI-Powered Kenya Safari & Beach Trip Planner",
        help_text="Site tagline for SEO"
    )
    meta_description = models.TextField(
        default="Plan your perfect Kenya safari, beach vacation & adventure with AI. Get personalized itineraries, weather forecasts & interactive maps.",
        help_text="Default meta description for SEO"
    )
    
    # Contact information
    support_email = models.EmailField(
        default='info@safarismart.co.ke',
        help_text="Support email address"
    )
    support_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Support phone number"
    )
    
    # Social media links
    facebook_url = models.URLField(
        blank=True,
        help_text="Facebook page URL"
    )
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter profile URL"
    )
    instagram_url = models.URLField(
        blank=True,
        help_text="Instagram profile URL"
    )
    youtube_url = models.URLField(
        blank=True,
        help_text="YouTube channel URL"
    )
    
    # Email notifications
    enable_email_notifications = models.BooleanField(
        default=True,
        help_text="Enable email notifications to users"
    )
    admin_notification_email = models.EmailField(
        default='admin@safarismart.co.ke',
        help_text="Email for admin notifications"
    )
    
    # API settings
    gemini_api_rate_limit = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1)],
        help_text="Gemini API requests per minute limit"
    )
    weather_api_cache_hours = models.IntegerField(
        default=6,
        validators=[MinValueValidator(1)],
        help_text="Hours to cache weather data"
    )
    
    # Version information
    app_version = models.CharField(
        max_length=20,
        default="1.0.0",
        help_text="Current application version"
    )
    last_deployment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last deployment date"
    )
    
    # Announcement banner
    show_announcement = models.BooleanField(
        default=False,
        help_text="Show announcement banner on homepage"
    )
    announcement_text = models.TextField(
        blank=True,
        help_text="Announcement text to display"
    )
    announcement_type = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Information'),
            ('warning', 'Warning'),
            ('success', 'Success'),
            ('danger', 'Alert')
        ],
        default='info',
        help_text="Announcement banner style"
    )
    announcement_link = models.URLField(
        blank=True,
        help_text="Optional link for announcement"
    )
    announcement_link_text = models.CharField(
        max_length=50,
        blank=True,
        default="Learn More",
        help_text="Text for announcement link"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Last updated by (username)"
    )
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"
        
    def __str__(self) -> str:
        return "System Configuration"
        
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        """Prevent deletion of configuration."""
        pass
        
    @classmethod
    def get_config(cls):
        """
        Get system configuration (Singleton).
        
        Returns:
            SystemConfiguration: The configuration instance
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config
        
    def clean(self):
        """Validate configuration values."""
        if self.max_trip_duration < self.min_trip_duration:
            raise ValidationError(
                "Maximum trip duration must be >= minimum"
            )
            
        if self.max_budget < self.min_budget:
            raise ValidationError(
                "Maximum budget must be >= minimum budget"
            )
            
        if self.max_adults < self.min_adults:
            raise ValidationError(
                "Maximum adults must be >= minimum adults"
            )



class ChatConfiguration(models.Model):
    """
    Configuration for trip planning chatbot.
    
    This model stores admin-configurable chat messages, settings,
    and behavior for the hybrid chat system (simple + AI).
    
    Singleton pattern ensures only one configuration exists.
    
    Attributes:
        is_enabled (bool): Enable/disable chat feature
        use_ai_for_complex (bool): Use AI for complex queries
        welcome_message (str): Initial greeting message
        destination_question (str): Question for destination
        duration_question (str): Question for trip duration
        budget_question (str): Question for budget level
        interests_question (str): Question for interests
        completion_message (str): Message when generating itinerary
        error_message (str): Message when bot doesn't understand
        ai_complexity_threshold (int): Word count to trigger AI
        
    Example:
        >>> config = ChatConfiguration.get_config()
        >>> print(config.welcome_message)
        'Hi! I'm your Safari planning assistant...'
    """
    
    # Enable/Disable Features
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enable chat feature for custom trip planning"
    )
    use_ai_for_complex = models.BooleanField(
        default=True,
        help_text="Use AI (Gemini) for complex user queries"
    )
    
    # Chat Messages
    welcome_message = models.TextField(
        default="Hi! I'm your Safari planning assistant. Tell me about your dream trip to Kenya! 🦁",
        help_text="First message users see when opening chat"
    )
    
    destination_question = models.TextField(
        default="Where would you like to go in Kenya?",
        help_text="Question asking for destination"
    )
    
    duration_question = models.TextField(
        default="How many days do you have for this trip?",
        help_text="Question asking for trip duration"
    )
    
    budget_question = models.TextField(
        default="What's your budget level?",
        help_text="Question asking for budget tier"
    )
    
    interests_question = models.TextField(
        default="What interests you most?",
        help_text="Question asking for travel interests"
    )
    
    completion_message = models.TextField(
        default="Perfect! Let me create your personalized itinerary... ✨",
        help_text="Message shown when generating itinerary"
    )
    
    error_message = models.TextField(
        default="Sorry, I didn't quite understand that. Could you rephrase?",
        help_text="Message when bot doesn't understand input"
    )
    
    # AI Configuration
    ai_complexity_threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        help_text="Minimum word count to trigger AI (lower = more AI usage, higher = more simple chat)"
    )
    
    max_chat_turns = models.IntegerField(
        default=10,
        validators=[MinValueValidator(3), MaxValueValidator(20)],
        help_text="Maximum conversation turns before forcing completion"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Chat Configuration"
        verbose_name_plural = "Chat Configuration"
        
    def __str__(self) -> str:
        return "Chat Configuration"
        
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        """Prevent deletion of configuration."""
        pass
        
    @classmethod
    def get_config(cls):
        """
        Get chat configuration (Singleton).
        
        Returns:
            ChatConfiguration: The configuration instance
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        config, created = cls.objects.get_or_create(pk=1)
        return config
        
    def clean(self):
        """Validate configuration values."""
        if self.ai_complexity_threshold < 5:
            raise ValidationError(
                "AI complexity threshold must be at least 5 words"
            )
            
        if self.max_chat_turns < 3:
            raise ValidationError(
                "Maximum chat turns must be at least 3"
            )
