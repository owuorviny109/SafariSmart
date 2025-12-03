"""
Module: services/analytics_service.py
Purpose: Service layer for analytics and social proof

This module contains service classes for calculating and displaying
analytics data including destination popularity and visit statistics.

Classes:
    DestinationAnalyticsService: Main analytics service
    VisitStatsCalculator: Calculates visit statistics
    TrendingDestinationsService: Identifies trending destinations
    
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from django.db.models import Count, Q
from django.utils import timezone

from core.models import Itinerary
from destinations.models import Destination


logger = logging.getLogger(__name__)


class VisitStatsCalculator:
    """
    Calculator for destination visit statistics.
    
    This class calculates various statistics about destination visits
    including monthly counts, trends, and popularity metrics.
    
    Attributes:
        None
        
    Example:
        >>> calculator = VisitStatsCalculator()
        >>> stats = calculator.calculate_monthly_visits("Maasai Mara")
        >>> print(stats['visit_count'])
        45
    """
    
    def calculate_monthly_visits(
        self,
        destination_name: str,
        months: int = 1
    ) -> Dict[str, int]:
        """
        Calculate visit statistics for a destination.
        
        Counts how many itineraries included this destination
        in the specified time period.
        
        Args:
            destination_name (str): Name of destination
            months (int): Number of months to look back
            
        Returns:
            Dict[str, int]: Visit statistics
            
        Example:
            >>> stats = calculator.calculate_monthly_visits("Nairobi", months=1)
            >>> print(f"{stats['visit_count']} people visited")
            45 people visited
        """
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months)
        
        # Count itineraries with this destination
        visit_count = Itinerary.objects.filter(
            destinations__name=destination_name,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).distinct().count()
        
        logger.debug(
            f"Calculated {visit_count} visits for {destination_name} "
            f"in last {months} month(s)"
        )
        
        return {
            'destination': destination_name,
            'visit_count': visit_count,
            'period_months': months,
            'start_date': start_date,
            'end_date': end_date
        }
        
    def calculate_total_visits(self, destination_name: str) -> int:
        """
        Calculate total all-time visits for a destination.
        
        Args:
            destination_name (str): Name of destination
            
        Returns:
            int: Total visit count
        """
        count = Itinerary.objects.filter(
            destinations__name=destination_name
        ).distinct().count()
        
        logger.debug(f"Total visits for {destination_name}: {count}")
        return count
        
    def calculate_visit_growth(
        self,
        destination_name: str
    ) -> Dict[str, any]:
        """
        Calculate visit growth trend for a destination.
        
        Compares current month to previous month to determine
        if destination is trending up or down.
        
        Args:
            destination_name (str): Name of destination
            
        Returns:
            Dict[str, any]: Growth statistics
            
        Example:
            >>> growth = calculator.calculate_visit_growth("Diani Beach")
            >>> print(f"Growth: {growth['percentage']}%")
            Growth: 25.5%
        """
        # Current month
        current_stats = self.calculate_monthly_visits(destination_name, months=1)
        current_count = current_stats['visit_count']
        
        # Previous month
        end_date = timezone.now() - timedelta(days=30)
        start_date = end_date - timedelta(days=30)
        
        previous_count = Itinerary.objects.filter(
            destinations__name=destination_name,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).distinct().count()
        
        # Calculate growth
        if previous_count > 0:
            growth_percentage = ((current_count - previous_count) / previous_count) * 100
        else:
            growth_percentage = 100 if current_count > 0 else 0
            
        is_trending = growth_percentage > 20  # 20% growth = trending
        
        return {
            'current_month': current_count,
            'previous_month': previous_count,
            'growth_percentage': round(growth_percentage, 1),
            'is_trending': is_trending
        }


class TrendingDestinationsService:
    """
    Service for identifying trending destinations.
    
    This class analyzes destination popularity and identifies
    which destinations are currently trending.
    
    Attributes:
        calculator (VisitStatsCalculator): Stats calculator
        
    Example:
        >>> service = TrendingDestinationsService()
        >>> trending = service.get_trending_destinations(limit=5)
        >>> print(trending[0]['name'])
        'Maasai Mara'
    """
    
    def __init__(
        self,
        calculator: Optional[VisitStatsCalculator] = None
    ):
        """
        Initialize trending destinations service.
        
        Args:
            calculator (VisitStatsCalculator, optional): Stats calculator
        """
        self.calculator = calculator or VisitStatsCalculator()
        
    def get_trending_destinations(
        self,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get list of trending destinations.
        
        Identifies destinations with highest growth in the last month.
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, any]]: Trending destinations with stats
            
        Example:
            >>> trending = service.get_trending_destinations(limit=5)
            >>> for dest in trending:
            ...     print(f"{dest['name']}: {dest['visit_count']} visits")
        """
        # Get all destinations with recent visits
        one_month_ago = timezone.now() - timedelta(days=30)
        
        trending = Itinerary.objects.filter(
            created_at__gte=one_month_ago
        ).values(
            'destinations__id',
            'destinations__name'
        ).annotate(
            visit_count=Count('id')
        ).order_by('-visit_count')[:limit]
        
        results = []
        for item in trending:
            if item['destinations__name']:
                results.append({
                    'id': item['destinations__id'],
                    'name': item['destinations__name'],
                    'visit_count': item['visit_count']
                })
                
        logger.info(f"Found {len(results)} trending destinations")
        return results
        
    def get_popular_destinations(
        self,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get most popular destinations of all time.
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, any]]: Popular destinations with stats
        """
        popular = Itinerary.objects.values(
            'destinations__id',
            'destinations__name'
        ).annotate(
            visit_count=Count('id')
        ).order_by('-visit_count')[:limit]
        
        results = []
        for item in popular:
            if item['destinations__name']:
                results.append({
                    'id': item['destinations__id'],
                    'name': item['destinations__name'],
                    'visit_count': item['visit_count']
                })
                
        logger.info(f"Found {len(results)} popular destinations")
        return results


class DestinationAnalyticsService:
    """
    Main service for destination analytics and social proof.
    
    This service orchestrates analytics operations and provides
    social proof data for display.
    
    Attributes:
        calculator (VisitStatsCalculator): Stats calculator
        trending_service (TrendingDestinationsService): Trending service
        
    Example:
        >>> service = DestinationAnalyticsService()
        >>> social_proof = service.get_social_proof_data("Maasai Mara")
        >>> print(social_proof['message'])
        '45 people visited Maasai Mara this month'
    """
    
    def __init__(
        self,
        calculator: Optional[VisitStatsCalculator] = None,
        trending_service: Optional[TrendingDestinationsService] = None
    ):
        """
        Initialize analytics service with dependencies.
        
        Args:
            calculator (VisitStatsCalculator, optional): Stats calculator
            trending_service (TrendingDestinationsService, optional): Trending service
        """
        self.calculator = calculator or VisitStatsCalculator()
        self.trending_service = trending_service or TrendingDestinationsService(
            self.calculator
        )
        
    def get_social_proof_data(
        self,
        destination_name: str
    ) -> Dict[str, any]:
        """
        Get social proof data for a destination.
        
        Creates formatted social proof message and statistics
        for display on itinerary pages.
        
        Args:
            destination_name (str): Name of destination
            
        Returns:
            Dict[str, any]: Social proof data
            
        Example:
            >>> data = service.get_social_proof_data("Nairobi")
            >>> print(data['message'])
            '45 people visited Nairobi this month'
        """
        # Get monthly stats
        stats = self.calculator.calculate_monthly_visits(destination_name)
        visit_count = stats['visit_count']
        
        # Get growth trend
        growth = self.calculator.calculate_visit_growth(destination_name)
        
        # Format message
        if visit_count == 0:
            message = f"Be the first to visit {destination_name}!"
        elif visit_count == 1:
            message = f"1 person visited {destination_name} this month"
        else:
            message = f"{visit_count} people visited {destination_name} this month"
            
        # Add trending badge if applicable
        badge = None
        if growth['is_trending']:
            badge = "🔥 Trending"
        elif visit_count > 50:
            badge = "⭐ Popular"
            
        social_proof = {
            'destination': destination_name,
            'visit_count': visit_count,
            'message': message,
            'badge': badge,
            'is_trending': growth['is_trending'],
            'growth_percentage': growth['growth_percentage']
        }
        
        logger.info(f"Generated social proof for {destination_name}")
        return social_proof
        
    def get_social_proof_for_destinations(
        self,
        destination_names: List[str]
    ) -> Dict[str, Dict]:
        """
        Get social proof data for multiple destinations.
        
        Args:
            destination_names (List[str]): List of destination names
            
        Returns:
            Dict[str, Dict]: Social proof data keyed by destination name
            
        Example:
            >>> destinations = ["Nairobi", "Mombasa", "Kisumu"]
            >>> data = service.get_social_proof_for_destinations(destinations)
            >>> print(data["Nairobi"]["message"])
            '45 people visited Nairobi this month'
        """
        social_proof_data = {}
        
        for destination in destination_names:
            try:
                data = self.get_social_proof_data(destination)
                social_proof_data[destination] = data
            except Exception as e:
                logger.warning(f"Failed to get social proof for {destination}: {e}")
                # Continue with other destinations
                
        logger.info(
            f"Generated social proof for {len(social_proof_data)}/{len(destination_names)} destinations"
        )
        return social_proof_data
        
    def get_itinerary_analytics(
        self,
        itinerary_id: int
    ) -> Dict[str, any]:
        """
        Get analytics data for an itinerary.
        
        Provides comprehensive analytics including view count,
        destination popularity, and trending status.
        
        Args:
            itinerary_id (int): Itinerary ID
            
        Returns:
            Dict[str, any]: Analytics data
            
        Raises:
            ValueError: If itinerary not found
        """
        try:
            itinerary = Itinerary.objects.get(id=itinerary_id)
        except Itinerary.DoesNotExist:
            raise ValueError(f"Itinerary {itinerary_id} not found")
            
        # Get destination names
        destination_names = list(
            itinerary.destinations.values_list('name', flat=True)
        )
        
        # Get social proof for all destinations
        social_proof = self.get_social_proof_for_destinations(destination_names)
        
        # Calculate average popularity
        total_visits = sum(
            data['visit_count'] for data in social_proof.values()
        )
        avg_visits = total_visits / len(destination_names) if destination_names else 0
        
        analytics = {
            'itinerary_id': itinerary_id,
            'view_count': itinerary.view_count,
            'destinations': social_proof,
            'total_destination_visits': total_visits,
            'average_visits_per_destination': round(avg_visits, 1),
            'has_trending_destinations': any(
                d['is_trending'] for d in social_proof.values()
            )
        }
        
        logger.info(f"Generated analytics for itinerary {itinerary_id}")
        return analytics
        
    def get_trending_summary(self) -> Dict[str, any]:
        """
        Get summary of trending destinations.
        
        Provides overview of current trending destinations
        for display on landing page or dashboard.
        
        Returns:
            Dict[str, any]: Trending summary
        """
        trending = self.trending_service.get_trending_destinations(limit=5)
        popular = self.trending_service.get_popular_destinations(limit=5)
        
        summary = {
            'trending_destinations': trending,
            'popular_destinations': popular,
            'total_itineraries': Itinerary.objects.count(),
            'this_month_itineraries': Itinerary.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        logger.info("Generated trending summary")
        return summary
