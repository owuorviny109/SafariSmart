"""
Module: services/itinerary_generator.py
Purpose: AI-powered itinerary generation using Google Gemini

This module provides itinerary generation services with AI integration
and template fallback for reliability.

Classes:
    GeminiItineraryGenerator: AI-powered itinerary generation
    TemplateItineraryGenerator: Template-based fallback
    ItineraryGeneratorFactory: Factory for selecting generator
  
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
        
        # Configure generation for faster responses
        generation_config = {
            'temperature': 0.7,  # Lower = more focused, faster
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2048,  # Limit output length for speed
        }
        
        # Use gemini-2.5-flash (fastest model)
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=generation_config
        )
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
            
            # Execute with rate limiting and timeout
            # Set a 20-second timeout to prevent 502 errors
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self.rate_limiter.execute,
                    'gemini',
                    self.model.generate_content,
                    prompt
                )
                try:
                    response = future.result(timeout=20)
                except concurrent.futures.TimeoutError:
                    logger.error("Gemini API call timed out after 20 seconds")
                    raise ItineraryGenerationError(
                        "AI generation timed out. Please try again.",
                        generator_type="ai"
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
        Build detailed prompt for Gemini AI with RAG and Intelligence.
        Requests JSON output for reliable parsing.
        """
        destinations = preferences.get('destinations', [])
        custom_destinations = preferences.get('custom_destinations', [])
        duration = preferences.get('duration_days', 3)
        budget = preferences.get('budget_amount', 50000)
        budget_category = preferences.get('budget_category', 'mid-range')
        adults = preferences.get('adults_count', 1)
        children = preferences.get('children_count', 0)
        interests = preferences.get('interests', [])
        
        # 1. RAG: Build Knowledge Base from DB
        destination_context = ""
        if destinations:
            destination_context = "KNOWN DESTINATION DATA (Use this for accuracy):\n"
            for dest in destinations:
                destination_context += (
                    f"- {dest.name}:\n"
                    f"  * Description: {dest.description}\n"
                    f"  * Best Time: {dest.best_time_to_visit}\n"
                    f"  * Est. Cost: {dest.average_cost_per_day} KSh/day\n"
                    f"  * Activities: {dest.popular_activities}\n"
                )

        # 2. OFFICIAL KWS FEES 2024 (Source: User Provided Documents)
        pricing_context = """
        OFFICIAL KWS CONSERVATION FEES (2024/2025):
        Use these EXACT figures. Do NOT estimate.

        1. PARK ENTRY FEES (Per Day):
           - PREMIUM PARKS (Amboseli, Lake Nakuru):
             * Citizen/Resident: Adult 860 KSh, Child 215 KSh
             * Non-Resident: Adult $60, Child $35
           - WILDERNESS PARKS A (Tsavo East & West):
             * Citizen/Resident: Adult 515 KSh, Child 215 KSh
             * Non-Resident: Adult $52, Child $35
           - WILDERNESS PARKS B (Meru, Aberdare, Mt. Kenya):
             * Citizen/Resident: Adult 300 KSh, Child 215 KSh
             * Non-Resident: Adult $52, Child $35
           - URBAN SAFARI (Nairobi National Park):
             * Citizen/Resident: Adult 430 KSh, Child 215 KSh
             * Non-Resident: Adult $43, Child $22
           - MARINE PARKS (Kisite Mpunguti):
             * Citizen/Resident: Adult 215 KSh, Child 125 KSh
             * Non-Resident: Adult $17, Child $13

        2. CAMPING FEES (Per Person Per Day):
           - SPECIAL CAMPSITES (Premium Parks):
             * Citizen/Resident: Adult 500 KSh, Child 250 KSh
             * Non-Resident: Adult $50, Child $25
           - SPECIAL CAMPSITES (Other Parks):
             * Citizen/Resident: Adult 250 KSh, Child 200 KSh
             * Non-Resident: Adult $35, Child $20
           - PUBLIC CAMPSITES (Premium Parks):
             * Citizen/Resident: Adult 250 KSh, Child 200 KSh
             * Non-Resident: Adult $30, Child $25
           - PUBLIC CAMPSITES (Other Parks):
             * Citizen/Resident: Adult 200 KSh, Child 150 KSh
             * Non-Resident: Adult $20, Child $15
           - Reservation Fees (Non-Refundable): 7,500 KSh

        3. VEHICLE FEES (Per Day):
           - Less than 6 seats: 300 KSh
           - 6-12 seats: 1,030 KSh
           - 13-24 seats: 2,585 KSh
           - 25-44 seats: 4,050 KSh
           - 45+ seats: 5,000 KSh

        4. SPECIAL ACTIVITIES (Per Person):
           - Night Game Drive: 2,155 KSh (per trip)
           - Lake Boating: 1,290 KSh (per hour)
           - Security/Guided Tours: 1,720 - 3,015 KSh (per guide up to 4hrs)
           - River Rafting: 1,720 KSh
           - Horse Riding (KWS horses): 2,585 KSh (excluding rider)
           - Private Horses: 1,030 KSh (per day)
           - Fishing (per line per day): 515 KSh (Mt. Kenya: 1,550 KSh)
           - Cycling: 215 KSh (per day)
           - Walking Safaris: 1,500 KSh (per person per day)

        5. OTHER CHARGES:
           - Event Security: 75,000 KSh
           - Vehicle Recovery: 7,500 KSh
           - Annual Passes (Adult): 43,100 KSh
        """

        prompt = f"""You are Juma, an expert Kenyan Safari Guide.
You don't just list places; you craft "Vibe-Matched" experiences.

USER PROFILE:
- Duration: {duration} days
- Budget: {budget} KSh ({budget_category})
- Travelers: {adults} Adults, {children} Children
- Interests: {', '.join(interests)}
- Selected Destinations: {', '.join([d.name for d in destinations])}
- Custom Requests: {', '.join(custom_destinations)}

{destination_context}

{pricing_context}

INSTRUCTIONS:
1. **Vibe Match:** Adjust the PACE and ACTIVITIES based on interests.
2. **Smart Budget:** Provide realistic costs based on the OFFICIAL KWS FEES above.
3. **Hidden Gem:** Suggest ONE unique alternative.

CRITICAL: You MUST output valid JSON only. No markdown formatting.
Follow this EXACT schema:

{{
  "title": "Catchy Trip Title",
  "summary": "2-3 sentences explaining the vibe.",
  "days": [
    {{
      "day": 1,
      "location": "Location Name",
      "theme": "Day Theme",
      "activities": [
        {{
          "time": "Morning",
          "activity": "Activity Name",
          "description": "Brief description",
          "cost": 5000
        }},
        {{
          "time": "Afternoon",
          "activity": "Activity Name",
          "description": "Brief description",
          "cost": 2000
        }},
        {{
          "time": "Evening",
          "activity": "Activity Name",
          "description": "Brief description",
          "cost": 0
        }}
      ],
      "accommodation": {{
        "name": "Hotel Name",
        "cost": 15000
      }}
    }}
  ],
  "budget_summary": {{
    "accommodation": 50000,
    "activities": 20000,
    "meals": 10000,
    "transport": 15000,
    "total": 95000
  }},
  "smart_tip": "Money saving tip here",
  "hidden_gem": "Hidden gem suggestion here"
}}
"""
        return prompt
        
    def _parse_response(
        self,
        response_text: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse AI JSON response into structured itinerary format.
        """
        import json
        import re
        
        try:
            # Clean response text (remove markdown code blocks if any)
            clean_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Parse JSON
            data = json.loads(clean_text)
            
            # Reconstruct text format for legacy compatibility
            content_text = f"# {data.get('title', 'My Safari')}\n\n"
            content_text += f"**Trip Summary:**\n{data.get('summary', '')}\n\n"
            content_text += "**Day-by-Day Plan:**\n\n"
            
            for day in data.get('days', []):
                content_text += f"**Day {day['day']}: {day['location']} - {day['theme']}**\n"
                for act in day.get('activities', []):
                    cost_str = f" (KSh {act['cost']})" if act.get('cost') else ""
                    content_text += f"*   **{act['time']}:** {act['activity']}{cost_str}\n"
                
                acc = day.get('accommodation', {})
                acc_cost = f" (Est. {acc.get('cost')} KSh)" if acc.get('cost') else ""
                content_text += f"*   **Stay:** {acc.get('name')}{acc_cost}\n\n"
            
            bs = data.get('budget_summary', {})
            content_text += "**Estimated Total Cost:**\n"
            content_text += f"Accommodation: KSh {bs.get('accommodation', 0)}\n"
            content_text += f"Activities: KSh {bs.get('activities', 0)}\n"
            content_text += f"Total: ~KSh {bs.get('total', 0)}\n\n"
            
            content_text += f"**Smart Budget Tip:**\n{data.get('smart_tip', '')}\n\n"
            content_text += f"**Hidden Gem Suggestion:**\n{data.get('hidden_gem', '')}\n"

            return {
                'title': data.get('title'),
                'duration_days': preferences.get('duration_days', 3),
                'destinations': [d.name for d in preferences.get('destinations', [])],
                'budget_amount': bs.get('total', preferences.get('budget_amount', 0)),
                'travelers': {
                    'adults': preferences.get('adults_count', 1),
                    'children': preferences.get('children_count', 0)
                },
                'content': content_text, # Legacy text support
                'structured_data': data, # New JSON support
                'generated_by': 'gemini-ai-json',
                'interests': preferences.get('interests', [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            # Fallback to raw text if JSON fails
            return {
                'title': self._generate_title(preferences),
                'content': response_text,
                'generated_by': 'gemini-ai-fallback',
                'destinations': [],
                'travelers': {},
                'budget_amount': 0
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
        custom_destinations = preferences.get('custom_destinations', [])
        duration = preferences.get('duration_days', 3)
        budget_category = preferences.get('budget_category', 'mid-range')
        interests = preferences.get('interests', [])
        
        # Combine all destination names
        all_dest_names = [dest.name for dest in destinations]
        all_dest_names.extend(custom_destinations)
        
        content = self._build_template_content(
            destinations,
            custom_destinations,
            duration,
            budget_category,
            interests
        )
        
        return {
            'title': self._generate_title(preferences),
            'duration_days': duration,
            'destinations': all_dest_names,
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
        custom_destinations: List[str],
        duration: int,
        budget_category: str,
        interests: List[str]
    ) -> str:
        """
        Build template itinerary content.
        
        Args:
            destinations: List of database destinations
            custom_destinations: List of custom destination names
            duration: Trip duration in days
            budget_category: Budget tier
            interests: User interests
            
        Returns:
            str: Formatted itinerary content
        """
        content_parts = []
        
        # Combine all destinations
        all_dest_names = [d.name for d in destinations]
        all_dest_names.extend(custom_destinations)
        total_destinations = len(all_dest_names)
        
        # Introduction
        dest_names = ", ".join(all_dest_names)
        content_parts.append(
            f"Welcome to your {duration}-day adventure in {dest_names}!\n\n"
        )
        
        # Daily itinerary
        days_per_dest = max(1, duration // total_destinations) if total_destinations else duration
        current_day = 1
        
        # Process database destinations
        for dest in destinations:
            for _ in range(days_per_dest):
                if current_day > duration:
                    break
                
                day_content = self._generate_day_template(
                    current_day,
                    dest,
                    budget_category,
                    interests
                )
                content_parts.append(day_content)
                current_day += 1
        
        # Process custom destinations
        for dest_name in custom_destinations:
            for _ in range(days_per_dest):
                if current_day > duration:
                    break
                
                day_content = self._generate_custom_day_template(
                    current_day,
                    dest_name,
                    budget_category,
                    interests
                )
                content_parts.append(day_content)
                current_day += 1
        
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
    
    def _generate_custom_day_template(
        self,
        day_number: int,
        destination_name: str,
        budget_category: str,
        interests: List[str]
    ) -> str:
        """Generate template for a custom destination day."""
        # Generic activities based on interests
        activity_suggestions = {
            'wildlife': 'Wildlife viewing and nature exploration',
            'culture': 'Cultural experiences and local community visits',
            'food': 'Local cuisine sampling and food tours',
            'adventure': 'Outdoor activities and adventure sports',
            'relaxation': 'Leisure activities and relaxation',
            'photography': 'Photography opportunities and scenic spots',
            'history': 'Historical landmarks and heritage sites',
            'nature': 'Nature walks and eco-tourism',
            'beach': 'Beach activities and water-based recreation',
            'nightlife': 'Evening entertainment and local nightlife'
        }
        
        # Select activities based on interests
        selected_activities = []
        for interest in interests[:2]:  # Take first 2 interests
            if interest in activity_suggestions:
                selected_activities.append(activity_suggestions[interest])
        
        if not selected_activities:
            selected_activities = ['Explore local attractions', 'Visit popular sites']
        
        # Budget-based accommodation
        accommodation_types = {
            'budget': 'Budget guesthouse or hostel',
            'mid-range': 'Mid-range hotel or lodge',
            'luxury': 'Luxury resort or boutique hotel'
        }
        accommodation = accommodation_types.get(budget_category, 'Local accommodation')
        
        return f"""Day {day_number}: {destination_name}

Morning (8:00 AM - 12:00 PM):
- Breakfast at your accommodation
- {selected_activities[0]}
- Explore the local area and main attractions

Afternoon (12:00 PM - 6:00 PM):
- Lunch at a recommended local restaurant
- {selected_activities[1] if len(selected_activities) > 1 else 'Visit nearby points of interest'}
- Afternoon sightseeing and activities

Evening (6:00 PM - 10:00 PM):
- Sunset viewing at a scenic spot
- Dinner featuring local specialties
- Evening leisure time

Accommodation: {accommodation} in {destination_name}
Estimated cost: KSh 3,000 - 8,000 per night (depending on season and availability)

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
        # Check if AI generation is enabled
        from django.conf import settings
        use_ai = getattr(settings, 'ENABLE_AI_GENERATION', True)
        
        if not use_ai:
            logger.info("AI generation disabled, using template generator")
            generator = TemplateItineraryGenerator()
            return generator.generate(preferences)
        
        try:
            # Try AI generation first
            logger.info("Attempting AI generation with Gemini")
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
