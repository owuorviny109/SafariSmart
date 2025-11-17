"""
Module: services/configuration_service.py
Purpose: Service for accessing admin-configurable settings

This module provides a clean interface for accessing configuration
data from the database, with caching for performance.

Classes:
    ConfigurationService: Singleton service for configuration access
    
Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from typing import List, Dict, Optional, Tuple
from django.core.cache import cache
from django.db.models import QuerySet

from core.models_config import (
    TravelType,
    BudgetCategory,
    InterestCategory,
    BudgetEstimate,
    SystemConfiguration
)


class ConfigurationService:
    """
    Service for accessing application configuration.
    
    This service provides cached access to configuration data stored
    in the database. Implements Singleton pattern and caching for
    optimal performance.
    
    Design Pattern: Singleton + Repository
    
    Attributes:
        _instance: Singleton instance
        _cache_timeout: Cache timeout in seconds (default: 300)
        
    Example:
        >>> config = ConfigurationService.get_instance()
        >>> travel_types = config.get_active_travel_types()
        >>> for travel_type in travel_types:
        ...     print(travel_type.name)
    """
    
    _instance = None
    _cache_timeout = 300  # 5 minutes
    
    def __new__(cls):
        """
        Create or return existing instance (Singleton pattern).
        
        Returns:
            ConfigurationService: Singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    @classmethod
    def get_instance(cls) -> 'ConfigurationService':
        """
        Get singleton instance.
        
        Returns:
            ConfigurationService: The service instance
        """
        return cls()
        
    def get_active_travel_types(self) -> QuerySet[TravelType]:
        """
        Get all active travel types.
        
        Returns cached results for performance.
        
        Returns:
            QuerySet[TravelType]: Active travel types ordered by sort_order
            
        Time Complexity: O(1) with cache, O(n) without
        Space Complexity: O(n) where n = number of travel types
        """
        cache_key = 'active_travel_types'
        travel_types = cache.get(cache_key)
        
        if travel_types is None:
            travel_types = list(
                TravelType.objects.filter(is_active=True)
                .order_by('sort_order', 'name')
            )
            cache.set(cache_key, travel_types, self._cache_timeout)
            
        return travel_types
        
    def get_travel_type_codes(self) -> List[str]:
        """
        Get list of valid travel type codes.
        
        Returns:
            List[str]: List of travel type codes (e.g., ['solo', 'family'])
            
        Time Complexity: O(n) where n = number of travel types
        Space Complexity: O(n)
        """
        travel_types = self.get_active_travel_types()
        return [tt.code for tt in travel_types]
        
    def is_valid_travel_type(self, code: str) -> bool:
        """
        Check if travel type code is valid.
        
        Args:
            code (str): Travel type code to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Time Complexity: O(n) where n = number of travel types
        Space Complexity: O(1)
        """
        return code in self.get_travel_type_codes()
        
    def get_active_budget_categories(self) -> QuerySet[BudgetCategory]:
        """
        Get all active budget categories.
        
        Returns:
            QuerySet[BudgetCategory]: Active categories ordered by sort_order
            
        Time Complexity: O(1) with cache, O(n) without
        Space Complexity: O(n)
        """
        cache_key = 'active_budget_categories'
        categories = cache.get(cache_key)
        
        if categories is None:
            categories = list(
                BudgetCategory.objects.filter(is_active=True)
                .order_by('sort_order', 'min_budget_per_day')
            )
            cache.set(cache_key, categories, self._cache_timeout)
            
        return categories
        
    def get_budget_category_codes(self) -> List[str]:
        """
        Get list of valid budget category codes.
        
        Returns:
            List[str]: List of budget codes (e.g., ['budget', 'mid-range'])
        """
        categories = self.get_active_budget_categories()
        return [cat.code for cat in categories]
        
    def is_valid_budget_category(self, code: str) -> bool:
        """
        Check if budget category code is valid.
        
        Args:
            code (str): Budget category code
            
        Returns:
            bool: True if valid, False otherwise
        """
        return code in self.get_budget_category_codes()
        
    def get_budget_estimate(
        self,
        budget_category_code: str
    ) -> Optional[BudgetEstimate]:
        """
        Get budget estimate for a category.
        
        Args:
            budget_category_code (str): Budget category code
            
        Returns:
            Optional[BudgetEstimate]: Budget estimate or None
            
        Time Complexity: O(1) with cache
        Space Complexity: O(1)
        """
        cache_key = f'budget_estimate_{budget_category_code}'
        estimate = cache.get(cache_key)
        
        if estimate is None:
            try:
                category = BudgetCategory.objects.get(
                    code=budget_category_code,
                    is_active=True
                )
                estimate = BudgetEstimate.objects.get(
                    budget_category=category
                )
                cache.set(cache_key, estimate, self._cache_timeout)
            except (BudgetCategory.DoesNotExist, BudgetEstimate.DoesNotExist):
                return None
                
        return estimate
        
    def get_budget_breakdown(
        self,
        budget_category_code: str
    ) -> Dict[str, Tuple[int, int]]:
        """
        Get budget breakdown ranges for a category.
        
        Args:
            budget_category_code (str): Budget category code
            
        Returns:
            Dict[str, Tuple[int, int]]: Breakdown with (min, max) tuples
            
        Example:
            >>> config = ConfigurationService.get_instance()
            >>> breakdown = config.get_budget_breakdown('mid-range')
            >>> print(breakdown['accommodation'])
            (10000, 15000)
        """
        estimate = self.get_budget_estimate(budget_category_code)
        
        if estimate is None:
            return {}
            
        return {
            'accommodation': (estimate.accommodation_min, estimate.accommodation_max),
            'activities': (estimate.activities_min, estimate.activities_max),
            'meals': (estimate.meals_min, estimate.meals_max),
            'transport': (estimate.transport_min, estimate.transport_max),
        }
        
    def get_active_interests(self) -> QuerySet[InterestCategory]:
        """
        Get all active interest categories.
        
        Returns:
            QuerySet[InterestCategory]: Active interests ordered by sort_order
        """
        cache_key = 'active_interests'
        interests = cache.get(cache_key)
        
        if interests is None:
            interests = list(
                InterestCategory.objects.filter(is_active=True)
                .order_by('sort_order', 'name')
            )
            cache.set(cache_key, interests, self._cache_timeout)
            
        return interests
        
    def get_interest_codes(self) -> List[str]:
        """
        Get list of valid interest codes.
        
        Returns:
            List[str]: List of interest codes
        """
        interests = self.get_active_interests()
        return [interest.code for interest in interests]
        
    def is_valid_interest(self, code: str) -> bool:
        """
        Check if interest code is valid.
        
        Args:
            code (str): Interest code
            
        Returns:
            bool: True if valid, False otherwise
        """
        return code in self.get_interest_codes()
        
    def get_system_config(self) -> SystemConfiguration:
        """
        Get system configuration.
        
        Returns:
            SystemConfiguration: System configuration instance
            
        Time Complexity: O(1) with cache
        Space Complexity: O(1)
        """
        cache_key = 'system_configuration'
        config = cache.get(cache_key)
        
        if config is None:
            config = SystemConfiguration.get_config()
            cache.set(cache_key, config, self._cache_timeout)
            
        return config
        
    def get_trip_duration_range(self) -> Tuple[int, int]:
        """
        Get valid trip duration range.
        
        Returns:
            Tuple[int, int]: (min_duration, max_duration)
        """
        config = self.get_system_config()
        return (config.min_trip_duration, config.max_trip_duration)
        
    def get_budget_range(self) -> Tuple[int, int]:
        """
        Get valid budget range.
        
        Returns:
            Tuple[int, int]: (min_budget, max_budget)
        """
        config = self.get_system_config()
        return (config.min_budget, config.max_budget)
        
    def get_traveler_constraints(self) -> Dict[str, int]:
        """
        Get traveler count constraints.
        
        Returns:
            Dict[str, int]: Constraints dictionary
        """
        config = self.get_system_config()
        return {
            'min_adults': config.min_adults,
            'max_adults': config.max_adults,
            'max_children': config.max_children,
            'max_total': config.max_total_travelers
        }
        
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature (str): Feature name (ai_generation, weather_forecasts, etc.)
            
        Returns:
            bool: True if enabled, False otherwise
        """
        config = self.get_system_config()
        feature_map = {
            'ai_generation': config.enable_ai_generation,
            'weather_forecasts': config.enable_weather_forecasts,
            'custom_destinations': config.enable_custom_destinations,
        }
        return feature_map.get(feature, False)
        
    def clear_cache(self) -> None:
        """
        Clear all configuration caches.
        
        Call this after updating configuration in admin.
        """
        cache_keys = [
            'active_travel_types',
            'active_budget_categories',
            'active_interests',
            'system_configuration',
        ]
        
        for key in cache_keys:
            cache.delete(key)
            
        # Clear budget estimate caches
        for category in BudgetCategory.objects.all():
            cache.delete(f'budget_estimate_{category.code}')

    
    def is_maintenance_mode(self) -> bool:
        """
        Check if system is in maintenance mode.
        
        Returns:
            bool: True if in maintenance mode
        """
        config = self.get_system_config()
        return config.maintenance_mode
        
    def get_maintenance_message(self) -> str:
        """
        Get maintenance mode message.
        
        Returns:
            str: Maintenance message
        """
        config = self.get_system_config()
        return config.maintenance_message
        
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Get rate limiting configuration.
        
        Returns:
            Dict[str, int]: Rate limit settings
        """
        config = self.get_system_config()
        return {
            'enabled': config.enable_rate_limiting,
            'per_hour': config.max_itineraries_per_hour,
            'per_day': config.max_itineraries_per_day
        }
        
    def get_announcement(self) -> Optional[Dict[str, str]]:
        """
        Get active announcement if enabled.
        
        Returns:
            Optional[Dict]: Announcement data or None
        """
        config = self.get_system_config()
        
        if not config.show_announcement:
            return None
            
        return {
            'text': config.announcement_text,
            'type': config.announcement_type,
            'link': config.announcement_link,
            'link_text': config.announcement_link_text
        }
        
    def get_seo_settings(self) -> Dict[str, str]:
        """
        Get SEO configuration.
        
        Returns:
            Dict[str, str]: SEO settings
        """
        config = self.get_system_config()
        return {
            'site_name': config.site_name,
            'site_tagline': config.site_tagline,
            'meta_description': config.meta_description
        }
        
    def get_social_links(self) -> Dict[str, str]:
        """
        Get social media links.
        
        Returns:
            Dict[str, str]: Social media URLs
        """
        config = self.get_system_config()
        return {
            'facebook': config.facebook_url,
            'twitter': config.twitter_url,
            'instagram': config.instagram_url,
            'youtube': config.youtube_url
        }
        
    def get_analytics_id(self) -> Optional[str]:
        """
        Get Google Analytics ID if enabled.
        
        Returns:
            Optional[str]: Analytics ID or None
        """
        config = self.get_system_config()
        
        if not config.enable_analytics:
            return None
            
        return config.google_analytics_id
