"""
Module: services/itinerary_generator.py
Purpose: AI-powered itinerary generation using Google Gemini

This module provides itinerary generation services with AI integration
and template fallback for reliability.

Classes:
    GeminiItineraryGenerator: AI-powered itinerary generation
    TemplateItineraryGenerator: Template-based fallback
    ItineraryGeneratorFactory: Factory for selecting generator
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
Updated: 2025-11-17 - Integrated BaseItineraryGenerator and ConfigurationService
"""

import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
import google.generativeai as genai

from destinations.models import Destination
from core.services.base_generator import BaseItineraryGenerator
from core.services.configuration_service import ConfigurationService
from core.services.rate_limiter import RateLimiter
from core.exceptions import AIServiceError, ItineraryGenerationError


logger = logging.getLogger(__name__)


class GeminiItineraryGenerator(BaseItineraryGenerator):
    """
    AI-powered itinerary generator using Google Gemini.
    
    This class generates personalized travel itineraries using
    Google's Gemini AI model based on user preferences.
    
    Inherits from BaseItineraryGenerator to ensure interface consistency.
    
    Attributes:
        model: Gemini generative model instance
        config: Configuration service instance
        
    Example:
        >>> generator = GeminiItineraryGenerator()
        >>> itinerary = generator.generate(preferences)
    """
    
    def __init__(self):
        """Initialize Gemini AI model, configuration service, and rate limiter."""
        api_key = settings.GEMINI_API_KEY
        
        if not api_key:
            raise AIServiceError(
                "GEMINI_API_KEY not configured. Add it to your .env file.",
                service_name="gemini"
            )
            
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash (latest free tier model)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.config = ConfigurationService.get_instance()
        self.rate_limiter = RateLimiter.get_instance()
        
    def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered itinerary based on user preferences.
        
        Validates preferences using base class before generation.
        
        Args:
            preferences (Dict[str, Any]): User preferences including:
                - destinations: List of Destination objects
                - duration_days: Trip duration
                - budget_amount: Total budget in KSh
                - budget_category: Budget tier
                - adults_count: Number of adults
                - children_count: Number of children
                - interests: List of interests
                
        Returns:
            Dict[str, Any]: Generated itinerary with daily activities
            
        Raises:
            ItineraryGenerationError: If AI generation fails
            WizardValidationError: If preferences are invalid
        """
        # Validate preferences using base class
        self.validate_preferences(preferences)
        
        try:
            prompt = self._build_prompt(preferences)
            
            logger.info("Generating itinerary with Gemini AI (rate-limited)")
            
            # Execute with rate limiting
            response = self.rate_limiter.execute(
                'gemini',
                self.model.generate_content,
                prompt
            )
            
            itinerary = self._parse_response(response.text, preferences)
            
            logger.info("Successfully generated AI itinerary")
            return itinerary
            
        except Exception as e:
            logger.error(f"Gemini AI generation failed: {str(e)}")
            raise ItineraryGenerationError(
                "Failed to generate itinerary with AI",
                generator_type="ai",
                original_error=e
            )
            
    def _build_prompt(self, preferences: Dict[str, Any]) -> str:
        """
        Build detailed prompt for Gemini AI.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            str: Formatted prompt for AI
        """
        destinations = preferences.get('destinations', [])
        duration = preferences.get('duration_days', 3)
        budget = preferences.get('budget_amount', 50000)
        budget_category = preferences.get('budget_category', 'mid-range')
        adults = preferences.get('adults_count', 1)
        children = preferences.get('children_count', 0)
        interests = preferences.get('interests', [])
        
        # Build destination details
        dest_details = []
        for dest in destinations:
            dest_details.append(
                f"- {dest.name}: {dest.description}"
            )
        destinations_text = "\n".join(dest_details)
        
        # Build interests text
        interests_text = ", ".join(interests) if interests else "general tourism"
        
        prompt = f"""You are a professional Kenyan safari and travel planner. Create a detailed {duration}-day itinerary for a trip to Kenya.

TRIP DETAILS:
- Destinations: 
{destinations_text}
- Duration: {duration} days
- Budget: KSh {budget:,} ({budget_category} tier)
- Travelers: {adults} adult(s), {children} child(ren)
- Interests: {interests_text}

REQUIREMENTS:
1. Create a day-by-day itinerary with specific activities
2. Include realistic timing for each activity
3. Suggest appropriate accommodations for {budget_category} budget
4. Include meal recommendations (breakfast, lunch, dinner)
5. Add estimated costs in KSh for major activities
6. Consider travel time between destinations
7. Make it family-friendly if children are present
8. Align activities with stated interests
9. Include practical tips and local insights
10. Keep total costs within budget

FORMAT YOUR RESPONSE AS:
Day 1: [Location]
Morning (8:00 AM - 12:00 PM):
- Activity 1 (Cost: KSh X)
- Activity 2

Afternoon (12:00 PM - 6:00 PM):
- Lunch at [Restaurant]
- Activity 3 (Cost: KSh X)

Evening (6:00 PM - 10:00 PM):
- Dinner at [Restaurant]
- Activity 4

Accommodation: [Hotel Name] (KSh X per night)

[Repeat for each day]

BUDGET BREAKDOWN:
- Accommodation: KSh X
- Activities: KSh X
- Meals: KSh X
- Transport: KSh X
Total: KSh X

TRAVEL TIPS:
- [Tip 1]
- [Tip 2]
- [Tip 3]

Generate a realistic, exciting, and practical itinerary."""

        return prompt
        
    def _parse_response(
        self,
        response_text: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse AI response into structured itinerary format.
        
        Args:
            response_text (str): Raw AI response
            preferences (Dict[str, Any]): Original preferences
            
        Returns:
            Dict[str, Any]: Structured itinerary data
        """
        return {
            'title': self._generate_title(preferences),
            'duration_days': preferences.get('duration_days', 3),
            'destinations': [
                dest.name for dest in preferences.get('destinations', [])
            ],
            'budget_amount': preferences.get('budget_amount', 0),
            'travelers': {
                'adults': preferences.get('adults_count', 1),
                'children': preferences.get('children_count', 0)
            },
            'content': response_text,
            'generated_by': 'gemini-ai',
            'interests': preferences.get('interests', [])
        }
        
    def _generate_title(self, preferences: Dict[str, Any]) -> str:
        """
        Generate itinerary title from preferences.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            str: Itinerary title
        """
        destinations = preferences.get('destinations', [])
        duration = preferences.get('duration_days', 3)
        
        if not destinations:
            return f"{duration}-Day Kenya Safari Adventure"
            
        if len(destinations) == 1:
            dest_name = destinations[0].name
            return f"{duration}-Day {dest_name} Experience"
            
        dest_names = " & ".join([d.name for d in destinations[:2]])
        if len(destinations) > 2:
            dest_names += f" + {len(destinations) - 2} more"
            
        return f"{duration}-Day {dest_names} Safari"


class TemplateItineraryGenerator(BaseItineraryGenerator):
    """
    Template-based itinerary generator as fallback.
    
    This class generates basic itineraries using predefined templates
    when AI generation fails or is unavailable.
    
    Inherits from BaseItineraryGenerator to ensure interface consistency.
    
    Attributes:
        config: Configuration service instance
    
    Example:
        >>> generator = TemplateItineraryGenerator()
        >>> itinerary = generator.generate(preferences)
    """
    
    def __init__(self):
        """Initialize configuration service."""
        self.config = ConfigurationService.get_instance()
    
    def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate template-based itinerary.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            Dict[str, Any]: Generated itinerary
        """
        logger.info("Generating template-based itinerary")
        
        destinations = preferences.get('destinations', [])
        duration = preferences.get('duration_days', 3)
        budget_category = preferences.get('budget_category', 'mid-range')
        interests = preferences.get('interests', [])
        
        content = self._build_template_content(
            destinations,
            duration,
            budget_category,
            interests
        )
        
        return {
            'title': self._generate_title(preferences),
            'duration_days': duration,
            'destinations': [dest.name for dest in destinations],
            'budget_amount': preferences.get('budget_amount', 0),
            'travelers': {
                'adults': preferences.get('adults_count', 1),
                'children': preferences.get('children_count', 0)
            },
            'content': content,
            'generated_by': 'template',
            'interests': interests
        }
        
    def _build_template_content(
        self,
        destinations: List[Destination],
        duration: int,
        budget_category: str,
        interests: List[str]
    ) -> str:
        """
        Build template itinerary content.
        
        Args:
            destinations: List of destinations
            duration: Trip duration in days
            budget_category: Budget tier
            interests: User interests
            
        Returns:
            str: Formatted itinerary content
        """
        content_parts = []
        
        # Introduction
        dest_names = ", ".join([d.name for d in destinations])
        content_parts.append(
            f"Welcome to your {duration}-day adventure in {dest_names}!\n\n"
        )
        
        # Daily itinerary
        days_per_dest = max(1, duration // len(destinations)) if destinations else duration
        
        current_day = 1
        for dest in destinations:
            dest_days = min(days_per_dest, duration - current_day + 1)
            
            for day_num in range(dest_days):
                day_content = self._generate_day_template(
                    current_day,
                    dest,
                    budget_category,
                    interests
                )
                content_parts.append(day_content)
                current_day += 1
                
                if current_day > duration:
                    break
                    
            if current_day > duration:
                break
        
        # Budget breakdown
        content_parts.append(self._generate_budget_template(budget_category))
        
        # Travel tips
        content_parts.append(self._generate_tips_template())
        
        return "\n".join(content_parts)
        
    def _generate_day_template(
        self,
        day_number: int,
        destination: Destination,
        budget_category: str,
        interests: List[str]
    ) -> str:
        """Generate template for a single day."""
        activities = self._get_activities_for_interests(
            destination,
            interests
        )
        
        accommodation = self._get_accommodation_suggestion(
            destination,
            budget_category
        )
        
        return f"""Day {day_number}: {destination.name}

Morning (8:00 AM - 12:00 PM):
- Breakfast at your accommodation
- {activities[0] if activities else 'Explore local attractions'}
- Morning game drive or guided tour

Afternoon (12:00 PM - 6:00 PM):
- Lunch at local restaurant
- {activities[1] if len(activities) > 1 else 'Visit cultural sites'}
- Afternoon activities and relaxation

Evening (6:00 PM - 10:00 PM):
- Sunset viewing
- Dinner at {accommodation}
- Evening entertainment

Accommodation: {accommodation}

"""
        
    def _get_activities_for_interests(
        self,
        destination: Destination,
        interests: List[str]
    ) -> List[str]:
        """Get activity suggestions based on interests."""
        activity_map = {
            'wildlife': 'Wildlife safari and game viewing',
            'culture': 'Cultural village visit and local interactions',
            'food': 'Local cuisine tasting and cooking class',
            'adventure': 'Hiking, climbing, or adventure sports',
            'relaxation': 'Spa treatment and leisure time',
            'photography': 'Photography tour and scenic viewpoints',
            'history': 'Historical sites and museum visits',
            'nature': 'Nature walks and bird watching',
            'beach': 'Beach activities and water sports',
            'nightlife': 'Evening entertainment and local nightlife'
        }
        
        activities = []
        for interest in interests:
            if interest in activity_map:
                activities.append(activity_map[interest])
                
        if not activities:
            activities = [
                'Explore local attractions',
                'Visit popular landmarks'
            ]
            
        return activities
        
    def _get_accommodation_suggestion(
        self,
        destination: Destination,
        budget_category: str
    ) -> str:
        """Get accommodation suggestion based on budget."""
        accommodation_map = {
            'budget': f'{destination.name} Budget Lodge or Guesthouse',
            'mid-range': f'{destination.name} Safari Lodge or Hotel',
            'luxury': f'{destination.name} Luxury Resort or Tented Camp'
        }
        
        return accommodation_map.get(
            budget_category,
            f'{destination.name} Accommodation'
        )
        
    def _generate_budget_template(self, budget_category: str) -> str:
        """
        Generate budget breakdown template using configuration service.
        
        Retrieves budget estimates from database instead of hardcoded values.
        
        Args:
            budget_category (str): Budget category code
            
        Returns:
            str: Formatted budget breakdown
        """
        # Get budget breakdown from configuration service
        breakdown = self.config.get_budget_breakdown(budget_category)
        
        if not breakdown:
            return "Budget estimates not available for this category.\n\n"
        
        return f"""ESTIMATED BUDGET BREAKDOWN (Per Day):
- Accommodation: KSh {breakdown['accommodation'][0]:,} - {breakdown['accommodation'][1]:,}
- Activities: KSh {breakdown['activities'][0]:,} - {breakdown['activities'][1]:,}
- Meals: KSh {breakdown['meals'][0]:,} - {breakdown['meals'][1]:,}
- Transport: KSh {breakdown['transport'][0]:,} - {breakdown['transport'][1]:,}

Note: Actual costs may vary based on season and availability.

"""
        
    def _generate_tips_template(self) -> str:
        """Generate travel tips template."""
        return """TRAVEL TIPS:
- Book accommodations in advance during peak season
- Carry sunscreen, hat, and comfortable walking shoes
- Respect local customs and wildlife viewing guidelines
- Keep emergency contacts and travel insurance handy
- Stay hydrated and follow health precautions
- Hire licensed guides for the best experience

Have a wonderful safari adventure in Kenya!
"""
        
    def _generate_title(self, preferences: Dict[str, Any]) -> str:
        """Generate itinerary title."""
        destinations = preferences.get('destinations', [])
        duration = preferences.get('duration_days', 3)
        
        if not destinations:
            return f"{duration}-Day Kenya Safari Adventure"
            
        if len(destinations) == 1:
            dest_name = destinations[0].name
            return f"{duration}-Day {dest_name} Experience"
            
        dest_names = " & ".join([d.name for d in destinations[:2]])
        if len(destinations) > 2:
            dest_names += f" + {len(destinations) - 2} more"
            
        return f"{duration}-Day {dest_names} Safari"


class ItineraryGeneratorFactory:
    """
    Factory for creating itinerary generators.
    
    This class provides a factory method to create the appropriate
    itinerary generator with automatic fallback to template generator
    if AI generation fails.
    
    Example:
        >>> generator = ItineraryGeneratorFactory.create()
        >>> itinerary = generator.generate(preferences)
    """
    
    @staticmethod
    def create(use_ai: bool = True) -> Any:
        """
        Create itinerary generator instance.
        
        Args:
            use_ai (bool): Whether to use AI generator (default: True)
            
        Returns:
            Generator instance (Gemini or Template)
        """
        if use_ai:
            try:
                return GeminiItineraryGenerator()
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Gemini generator: {str(e)}. "
                    "Falling back to template generator."
                )
                return TemplateItineraryGenerator()
        else:
            return TemplateItineraryGenerator()
            
    @staticmethod
    def generate_with_fallback(preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate itinerary with automatic fallback.
        
        Tries AI generation first, falls back to template if it fails.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            Dict[str, Any]: Generated itinerary
        """
        try:
            # Try AI generation first
            generator = GeminiItineraryGenerator()
            return generator.generate(preferences)
            
        except Exception as e:
            logger.warning(
                f"AI generation failed: {str(e)}. "
                "Using template fallback."
            )
            
            # Fallback to template
            generator = TemplateItineraryGenerator()
            return generator.generate(preferences)
