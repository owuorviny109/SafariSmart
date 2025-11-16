"""
Module: services/itinerary_display_service.py
Purpose: Service layer for itinerary display and formatting

This module contains service classes for handling itinerary display logic,
including content formatting, route visualization, and cost breakdown.

Classes:
    ItineraryDisplayService: Main service for itinerary display operations
    RouteVisualizationService: Handles route visualization logic
    CostBreakdownService: Handles cost breakdown calculations
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

from core.models import Itinerary
from destinations.models import Destination


logger = logging.getLogger(__name__)


class RouteVisualizationService:
    """
    Service for generating route visualization data.
    
    This service creates structured data for displaying travel routes
    between destinations in a visual timeline format.
    
    Attributes:
        None
        
    Example:
        >>> service = RouteVisualizationService()
        >>> route_data = service.generate_route_data(destinations)
        >>> print(route_data[0]['name'])
        'Maasai Mara'
    """
    
    def generate_route_data(
        self,
        destinations: List[Destination]
    ) -> List[Dict[str, str]]:
        """
        Generate route visualization data from destinations.
        
        Creates a list of route items with destination information
        formatted for display in a visual timeline.
        
        Args:
            destinations (List[Destination]): Ordered list of destinations
            
        Returns:
            List[Dict[str, str]]: Route data with name, type, county
            
        Example:
            >>> destinations = [maasai_mara, diani_beach]
            >>> route_data = service.generate_route_data(destinations)
            >>> len(route_data)
            2
        """
        if not destinations:
            logger.warning("No destinations provided for route visualization")
            return []
            
        route_data = []
        
        for destination in destinations:
            route_item = {
                'name': destination.name,
                'type': destination.destination_type.title(),
                'county': destination.county or 'Kenya',
                'icon': self._get_destination_icon(destination.destination_type)
            }
            route_data.append(route_item)
            
        logger.info(f"Generated route data for {len(route_data)} destinations")
        return route_data
        
    def _get_destination_icon(self, destination_type: str) -> str:
        """
        Get Bootstrap icon class for destination type.
        
        Args:
            destination_type (str): Type of destination
            
        Returns:
            str: Bootstrap icon class name
        """
        icon_map = {
            'safari': 'binoculars-fill',
            'beach': 'umbrella-fill',
            'city': 'building-fill',
            'mountain': 'triangle-fill',
            'cultural': 'bank-fill',
            'adventure': 'lightning-fill'
        }
        
        return icon_map.get(destination_type.lower(), 'geo-alt-fill')


class CostBreakdownService:
    """
    Service for calculating and formatting cost breakdowns.
    
    This service handles cost breakdown calculations and formatting
    for display in itinerary views.
    
    Attributes:
        None
        
    Example:
        >>> service = CostBreakdownService()
        >>> breakdown = service.calculate_breakdown(itinerary)
        >>> print(breakdown['accommodation'])
        Decimal('50000')
    """
    
    def calculate_breakdown(
        self,
        itinerary: Itinerary
    ) -> Dict[str, Decimal]:
        """
        Calculate cost breakdown from itinerary data.
        
        Extracts and formats cost breakdown from itinerary's
        cost_breakdown field or generates default breakdown.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            Dict[str, Decimal]: Cost breakdown by category
            
        Example:
            >>> breakdown = service.calculate_breakdown(itinerary)
            >>> 'accommodation' in breakdown
            True
        """
        if not itinerary.cost_breakdown:
            logger.info("No cost breakdown available, generating default")
            return self._generate_default_breakdown(itinerary)
            
        # Convert to Decimal for precision
        breakdown = {}
        for category, amount in itinerary.cost_breakdown.items():
            breakdown[category] = Decimal(str(amount))
            
        logger.info(f"Calculated breakdown with {len(breakdown)} categories")
        return breakdown
        
    def _generate_default_breakdown(
        self,
        itinerary: Itinerary
    ) -> Dict[str, Decimal]:
        """
        Generate default cost breakdown based on budget category.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            Dict[str, Decimal]: Default cost breakdown
        """
        total = Decimal(str(itinerary.total_budget))
        
        # Default percentages by category
        percentages = {
            'budget': {
                'accommodation': Decimal('0.35'),
                'activities': Decimal('0.30'),
                'meals': Decimal('0.20'),
                'transport': Decimal('0.15')
            },
            'mid-range': {
                'accommodation': Decimal('0.40'),
                'activities': Decimal('0.30'),
                'meals': Decimal('0.20'),
                'transport': Decimal('0.10')
            },
            'luxury': {
                'accommodation': Decimal('0.50'),
                'activities': Decimal('0.25'),
                'meals': Decimal('0.15'),
                'transport': Decimal('0.10')
            }
        }
        
        category_percentages = percentages.get(
            itinerary.budget_category,
            percentages['mid-range']
        )
        
        breakdown = {}
        for category, percentage in category_percentages.items():
            breakdown[category] = total * percentage
            
        return breakdown
        
    def format_breakdown_for_display(
        self,
        breakdown: Dict[str, Decimal]
    ) -> List[Tuple[str, str]]:
        """
        Format cost breakdown for template display.
        
        Args:
            breakdown (Dict[str, Decimal]): Cost breakdown
            
        Returns:
            List[Tuple[str, str]]: Formatted (category, amount) pairs
            
        Example:
            >>> formatted = service.format_breakdown_for_display(breakdown)
            >>> formatted[0]
            ('Accommodation', 'KSh 50,000')
        """
        formatted = []
        
        for category, amount in breakdown.items():
            formatted_category = category.replace('_', ' ').title()
            formatted_amount = f"KSh {amount:,.0f}"
            formatted.append((formatted_category, formatted_amount))
            
        return formatted


class ItineraryDisplayService:
    """
    Main service for itinerary display operations.
    
    This service orchestrates all display-related operations including
    content formatting, route visualization, and cost breakdown.
    
    Attributes:
        route_service (RouteVisualizationService): Route visualization service
        cost_service (CostBreakdownService): Cost breakdown service
        
    Example:
        >>> service = ItineraryDisplayService()
        >>> display_data = service.prepare_display_data(itinerary)
        >>> print(display_data['title'])
        '7-Day Maasai Mara Safari'
    """
    
    def __init__(
        self,
        route_service: Optional[RouteVisualizationService] = None,
        cost_service: Optional[CostBreakdownService] = None,
        analytics_service: Optional['DestinationAnalyticsService'] = None,
        weather_service: Optional['WeatherService'] = None
    ):
        """
        Initialize display service with dependencies.
        
        Args:
            route_service (RouteVisualizationService, optional): Route service
            cost_service (CostBreakdownService, optional): Cost service
            analytics_service (DestinationAnalyticsService, optional): Analytics service
            weather_service (WeatherService, optional): Weather service
        """
        self.route_service = route_service or RouteVisualizationService()
        self.cost_service = cost_service or CostBreakdownService()
        
        # Import here to avoid circular dependency
        if analytics_service is None:
            from core.services.analytics_service import DestinationAnalyticsService
            analytics_service = DestinationAnalyticsService()
        self.analytics_service = analytics_service
        
        # Import weather service
        if weather_service is None:
            from core.services.weather_service import WeatherService, WeatherAPIException
            try:
                weather_service = WeatherService()
            except WeatherAPIException as e:
                logger.warning(f"Weather service not available: {e}")
                weather_service = None
        self.weather_service = weather_service
        
    def prepare_display_data(
        self,
        itinerary: Itinerary
    ) -> Dict[str, any]:
        """
        Prepare all data needed for itinerary display.
        
        This method orchestrates the preparation of all display data
        including route visualization, cost breakdown, and metadata.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            Dict[str, any]: Complete display data
            
        Raises:
            ValueError: If itinerary is invalid
            
        Example:
            >>> display_data = service.prepare_display_data(itinerary)
            >>> 'route_data' in display_data
            True
        """
        self._validate_itinerary(itinerary)
        
        logger.info(f"Preparing display data for itinerary {itinerary.id}")
        
        # Get destinations
        destinations = list(itinerary.destinations.all())
        
        # Generate route visualization data
        route_data = self.route_service.generate_route_data(destinations)
        
        # Calculate cost breakdown
        cost_breakdown = self.cost_service.calculate_breakdown(itinerary)
        formatted_costs = self.cost_service.format_breakdown_for_display(
            cost_breakdown
        )
        
        # Extract content and metadata
        content = self._extract_content(itinerary)
        generated_by = self._extract_generated_by(itinerary)
        
        # Get social proof data for destinations
        destination_names = [d.name for d in destinations]
        social_proof = self.analytics_service.get_social_proof_for_destinations(
            destination_names
        )
        
        # Get weather data for destinations (if available)
        weather_data = self._get_weather_data(destination_names)
        
        display_data = {
            'itinerary': itinerary,
            'route_data': route_data,
            'cost_breakdown': formatted_costs,
            'content': content,
            'generated_by': generated_by,
            'is_ai_generated': generated_by == 'gemini-ai',
            'destination_count': len(destinations),
            'total_cost': itinerary.total_budget,
            'social_proof': social_proof,
            'weather_data': weather_data
        }
        
        logger.info("Display data prepared successfully with social proof and weather")
        return display_data
        
    def _validate_itinerary(self, itinerary: Itinerary) -> None:
        """
        Validate itinerary instance.
        
        Args:
            itinerary (Itinerary): Itinerary to validate
            
        Raises:
            ValueError: If itinerary is invalid
        """
        if not itinerary:
            raise ValueError("Itinerary cannot be None")
            
        if not itinerary.itinerary_data:
            raise ValueError("Itinerary data is missing")
            
    def _extract_content(self, itinerary: Itinerary) -> str:
        """
        Extract content from itinerary data.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            str: Itinerary content
        """
        if isinstance(itinerary.itinerary_data, dict):
            return itinerary.itinerary_data.get('content', '')
        return str(itinerary.itinerary_data)
        
    def _extract_generated_by(self, itinerary: Itinerary) -> str:
        """
        Extract generation method from itinerary data.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            str: Generation method ('gemini-ai' or 'template')
        """
        if isinstance(itinerary.itinerary_data, dict):
            return itinerary.itinerary_data.get('generated_by', 'template')
        return 'template'
        
    def _get_weather_data(self, destination_names: List[str]) -> Dict[str, Dict]:
        """
        Get weather data for destinations.
        
        Fetches weather data if service is available, otherwise returns empty dict.
        
        Args:
            destination_names (List[str]): List of destination names
            
        Returns:
            Dict[str, Dict]: Weather data keyed by destination name
        """
        if not self.weather_service:
            logger.debug("Weather service not available, skipping weather data")
            return {}
            
        try:
            weather_data = self.weather_service.get_weather_for_destinations(
                destination_names
            )
            logger.info(f"Fetched weather for {len(weather_data)} destinations")
            return weather_data
        except Exception as e:
            logger.warning(f"Failed to fetch weather data: {e}")
            return {}
