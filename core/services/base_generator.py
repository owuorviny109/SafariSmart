"""
Module: services/base_generator.py
Purpose: Abstract base class for itinerary generators

This module defines the interface contract that all itinerary generators
must implement, ensuring consistency and enabling polymorphism.

Classes:
    BaseItineraryGenerator: Abstract base class for generators
    
Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from destinations.models import Destination


class BaseItineraryGenerator(ABC):
    """
    Abstract base class for itinerary generators.
    
    This class defines the interface that all itinerary generators must
    implement. It ensures consistency across different generation strategies
    (AI-based, template-based, hybrid, etc.) and enables polymorphic usage.
    
    All concrete generator classes must implement the generate() method.
    
    Design Pattern: Strategy Pattern
    - Defines a family of algorithms (generation strategies)
    - Encapsulates each algorithm
    - Makes algorithms interchangeable
    
    Example:
        >>> class CustomGenerator(BaseItineraryGenerator):
        ...     def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        ...         # Custom generation logic
        ...         return itinerary_data
        ...
        >>> generator = CustomGenerator()
        >>> itinerary = generator.generate(preferences)
    """
    
    @abstractmethod
    def generate(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate itinerary from user preferences.
        
        This method must be implemented by all concrete generator classes.
        It takes user preferences and returns a structured itinerary.
        
        Args:
            preferences (Dict[str, Any]): User preferences including:
                - destinations (List[Destination]): Selected destinations
                - custom_destinations (List[str]): Custom destination names
                - duration_days (int): Trip duration in days
                - start_date (str, optional): Start date (YYYY-MM-DD)
                - end_date (str, optional): End date (YYYY-MM-DD)
                - budget_amount (int): Total budget in KSh
                - budget_category (str): Budget tier (budget/mid-range/luxury)
                - adults_count (int): Number of adults
                - children_count (int): Number of children
                - travel_type (str): Travel type (solo/family/couple/friends)
                - interests (List[str]): User interests
                
        Returns:
            Dict[str, Any]: Generated itinerary with structure:
                - title (str): Itinerary title
                - duration_days (int): Trip duration
                - destinations (List[str]): Destination names
                - budget_amount (int): Total budget
                - travelers (Dict): Traveler counts
                - content (str): Formatted itinerary content
                - generated_by (str): Generator identifier
                - interests (List[str]): User interests
                
        Raises:
            ItineraryGenerationError: If generation fails
            WizardValidationError: If preferences are invalid
            
        Example:
            >>> preferences = {
            ...     'destinations': [maasai_mara, diani_beach],
            ...     'duration_days': 7,
            ...     'budget_amount': 150000,
            ...     'budget_category': 'mid-range',
            ...     'adults_count': 2,
            ...     'children_count': 1,
            ...     'interests': ['wildlife', 'beach']
            ... }
            >>> itinerary = generator.generate(preferences)
            >>> print(itinerary['title'])
            '7-Day Maasai Mara & Diani Beach Safari'
        """
        pass
        
    def validate_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Validate user preferences before generation.
        
        This method provides common validation logic that can be used
        by all generator implementations. Subclasses can override to
        add additional validation.
        
        Args:
            preferences (Dict[str, Any]): User preferences to validate
            
        Raises:
            WizardValidationError: If preferences are invalid
            
        Time Complexity: O(n) where n = number of destinations
        Space Complexity: O(1)
        """
        from core.exceptions import WizardValidationError
        
        # Validate required fields
        required_fields = [
            'duration_days',
            'budget_amount',
            'budget_category',
            'adults_count',
            'children_count'
        ]
        
        for field in required_fields:
            if field not in preferences:
                raise WizardValidationError(
                    f"Missing required field: {field}",
                    field=field
                )
        
        # Validate at least one destination
        destinations = preferences.get('destinations', [])
        custom_destinations = preferences.get('custom_destinations', [])
        
        if not destinations and not custom_destinations:
            raise WizardValidationError(
                "At least one destination must be selected",
                field="destinations"
            )
        
        # Validate duration
        duration = preferences.get('duration_days', 0)
        if not isinstance(duration, int) or duration < 1 or duration > 30:
            raise WizardValidationError(
                "Duration must be between 1 and 30 days",
                field="duration_days",
                value=duration
            )
        
        # Validate budget
        budget = preferences.get('budget_amount', 0)
        if not isinstance(budget, int) or budget < 10000:
            raise WizardValidationError(
                "Budget must be at least KSh 10,000",
                field="budget_amount",
                value=budget
            )
        
        # Validate traveler counts
        adults = preferences.get('adults_count', 0)
        children = preferences.get('children_count', 0)
        
        if not isinstance(adults, int) or adults < 1:
            raise WizardValidationError(
                "At least 1 adult is required",
                field="adults_count",
                value=adults
            )
        
        if not isinstance(children, int) or children < 0:
            raise WizardValidationError(
                "Children count cannot be negative",
                field="children_count",
                value=children
            )
        
    def _generate_title(self, preferences: Dict[str, Any]) -> str:
        """
        Generate itinerary title from preferences.
        
        This helper method creates a descriptive title based on
        destinations and duration. Can be overridden by subclasses.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            str: Generated title
            
        Time Complexity: O(n) where n = number of destinations
        Space Complexity: O(n)
        """
        destinations = preferences.get('destinations', [])
        custom_destinations = preferences.get('custom_destinations', [])
        duration = preferences.get('duration_days', 3)
        
        # Combine all destination names
        all_dest_names = []
        
        # Add database destinations
        if destinations:
            all_dest_names.extend([dest.name for dest in destinations])
        
        # Add custom destinations
        if custom_destinations:
            all_dest_names.extend(custom_destinations)
        
        # Generate title based on destination count
        if not all_dest_names:
            return f"{duration}-Day Kenya Safari Adventure"
        
        if len(all_dest_names) == 1:
            return f"{duration}-Day {all_dest_names[0]} Experience"
        
        # Show first two destinations
        dest_text = " & ".join(all_dest_names[:2])
        
        # Add count if more than 2
        if len(all_dest_names) > 2:
            dest_text += f" + {len(all_dest_names) - 2} more"
        
        return f"{duration}-Day {dest_text} Safari"
        
    def _extract_destination_names(
        self,
        preferences: Dict[str, Any]
    ) -> List[str]:
        """
        Extract all destination names from preferences.
        
        Combines both database destinations and custom destinations
        into a single list of names.
        
        Args:
            preferences (Dict[str, Any]): User preferences
            
        Returns:
            List[str]: All destination names
            
        Time Complexity: O(n) where n = number of destinations
        Space Complexity: O(n)
        """
        names = []
        
        # Add database destination names
        destinations = preferences.get('destinations', [])
        if destinations:
            names.extend([dest.name for dest in destinations])
        
        # Add custom destination names
        custom_destinations = preferences.get('custom_destinations', [])
        if custom_destinations:
            names.extend(custom_destinations)
        
        return names
        
    def __str__(self) -> str:
        """Return string representation of generator."""
        return f"{self.__class__.__name__}"
        
    def __repr__(self) -> str:
        """Return detailed representation of generator."""
        return f"<{self.__class__.__name__}>"
