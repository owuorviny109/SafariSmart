"""
Module: services/share_service.py
Purpose: Service layer for itinerary sharing functionality

This module contains service classes for handling itinerary sharing,
including URL generation and share tracking.

Classes:
    ShareService: Main service for sharing operations
    ShareURLGenerator: Generates shareable URLs
    ShareTracker: Tracks share statistics
    
 
"""

from typing import Dict, Optional
from urllib.parse import urljoin
import logging

from django.conf import settings
from django.urls import reverse

from core.models import Itinerary


logger = logging.getLogger(__name__)


class ShareURLGenerator:
    """
    Service for generating shareable URLs.
    
    This service creates properly formatted URLs for sharing itineraries
    across different platforms and contexts.
    
    Attributes:
        base_url (str): Base URL for the application
        
    Example:
        >>> generator = ShareURLGenerator()
        >>> url = generator.generate_share_url(itinerary)
        >>> print(url)
        'https://safarismart.co.ke/itinerary/abc-123/'
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize URL generator.
        
        Args:
            base_url (str, optional): Base URL, defaults to settings
        """
        self.base_url = base_url or self._get_base_url()
        
    def _get_base_url(self) -> str:
        """
        Get base URL from settings or default.
        
        Returns:
            str: Base URL for the application
        """
        # In production, this should come from settings
        # For development, use localhost
        if settings.DEBUG:
            return 'http://127.0.0.1:8000'
        return getattr(settings, 'BASE_URL', 'https://safarismart.co.ke')
        
    def generate_share_url(
        self,
        itinerary: Itinerary,
        absolute: bool = True
    ) -> str:
        """
        Generate shareable URL for itinerary.
        
        Creates a full URL that can be shared via social media,
        messaging apps, or copied to clipboard.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            absolute (bool): Whether to return absolute URL
            
        Returns:
            str: Shareable URL
            
        Example:
            >>> url = generator.generate_share_url(itinerary)
            >>> 'itinerary' in url
            True
        """
        # Generate relative URL
        relative_url = reverse(
            'core:itinerary_detail',
            kwargs={'share_code': str(itinerary.share_code)}
        )
        
        if not absolute:
            return relative_url
            
        # Make absolute URL
        absolute_url = urljoin(self.base_url, relative_url)
        
        logger.info(f"Generated share URL for itinerary {itinerary.id}")
        return absolute_url
        
    def generate_social_share_data(
        self,
        itinerary: Itinerary
    ) -> Dict[str, str]:
        """
        Generate data for social media sharing.
        
        Creates structured data optimized for sharing on social
        platforms with proper titles, descriptions, and URLs.
        
        Args:
            itinerary (Itinerary): Itinerary instance
            
        Returns:
            Dict[str, str]: Social share data
            
        Example:
            >>> data = generator.generate_social_share_data(itinerary)
            >>> print(data['title'])
            '7-Day Maasai Mara Safari'
        """
        url = self.generate_share_url(itinerary)
        
        # Create engaging share text
        destination_names = ', '.join([
            d.name for d in itinerary.destinations.all()[:2]
        ])
        
        if itinerary.destinations.count() > 2:
            destination_names += f" + {itinerary.destinations.count() - 2} more"
            
        share_data = {
            'title': itinerary.title,
            'text': (
                f"Check out my {itinerary.duration_days}-day Kenya adventure "
                f"to {destination_names}! 🦁🌍"
            ),
            'url': url,
            'hashtags': 'KenyaSafari,TravelKenya,SafariSmart'
        }
        
        return share_data


class ShareTracker:
    """
    Service for tracking share statistics.
    
    This service tracks when and how itineraries are shared,
    providing analytics for popular destinations and trips.
    
    Attributes:
        None
        
    Example:
        >>> tracker = ShareTracker()
        >>> tracker.track_share(itinerary, 'whatsapp')
    """
    
    def track_share(
        self,
        itinerary: Itinerary,
        platform: str = 'unknown'
    ) -> None:
        """
        Track itinerary share event.
        
        Records share events for analytics and popularity tracking.
        Currently logs the event; can be extended to store in database.
        
        Args:
            itinerary (Itinerary): Shared itinerary
            platform (str): Platform used for sharing
            
        Example:
            >>> tracker.track_share(itinerary, 'facebook')
        """
        logger.info(
            f"Itinerary {itinerary.id} shared via {platform} "
            f"(share_code: {itinerary.share_code})"
        )
        
        # Future: Store in ShareEvent model for analytics
        # ShareEvent.objects.create(
        #     itinerary=itinerary,
        #     platform=platform,
        #     timestamp=timezone.now()
        # )


class ShareService:
    """
    Main service for itinerary sharing operations.
    
    This service orchestrates all sharing-related operations including
    URL generation, social media data preparation, and share tracking.
    
    Attributes:
        url_generator (ShareURLGenerator): URL generation service
        tracker (ShareTracker): Share tracking service
        
    Example:
        >>> service = ShareService()
        >>> share_data = service.prepare_share_data(itinerary)
        >>> print(share_data['url'])
        'https://safarismart.co.ke/itinerary/abc-123/'
    """
    
    def __init__(
        self,
        url_generator: Optional[ShareURLGenerator] = None,
        tracker: Optional[ShareTracker] = None
    ):
        """
        Initialize share service with dependencies.
        
        Args:
            url_generator (ShareURLGenerator, optional): URL generator
            tracker (ShareTracker, optional): Share tracker
        """
        self.url_generator = url_generator or ShareURLGenerator()
        self.tracker = tracker or ShareTracker()
        
    def prepare_share_data(
        self,
        itinerary: Itinerary
    ) -> Dict[str, str]:
        """
        Prepare all data needed for sharing.
        
        This method orchestrates the preparation of all sharing data
        including URLs, social media text, and metadata.
        
        Args:
            itinerary (Itinerary): Itinerary to share
            
        Returns:
            Dict[str, str]: Complete share data
            
        Raises:
            ValueError: If itinerary is invalid
            
        Example:
            >>> share_data = service.prepare_share_data(itinerary)
            >>> 'url' in share_data
            True
        """
        self._validate_itinerary(itinerary)
        
        logger.info(f"Preparing share data for itinerary {itinerary.id}")
        
        # Generate social share data
        share_data = self.url_generator.generate_social_share_data(itinerary)
        
        # Add additional metadata
        share_data['share_code'] = str(itinerary.share_code)
        share_data['duration'] = itinerary.duration_days
        share_data['destination_count'] = itinerary.destinations.count()
        
        logger.info("Share data prepared successfully")
        return share_data
        
    def record_share(
        self,
        itinerary: Itinerary,
        platform: str = 'unknown'
    ) -> None:
        """
        Record a share event.
        
        Tracks when an itinerary is shared for analytics purposes.
        
        Args:
            itinerary (Itinerary): Shared itinerary
            platform (str): Platform used for sharing
            
        Example:
            >>> service.record_share(itinerary, 'twitter')
        """
        self.tracker.track_share(itinerary, platform)
        
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
            
        if not itinerary.share_code:
            raise ValueError("Itinerary must have a share code")
