"""
Module: services/destination_enrichment.py
Purpose: Enrich destinations with data from free APIs

This module provides services to automatically enrich destination
information using free, legal APIs.

APIs Used:
- Wikipedia API (100% free, no limits)
- OpenTripMap API (free, 1000 requests/day)
- Nominatim/OpenStreetMap (free geocoding)

Author: SafariSmart Kenya Team
Date: 2025-11-17
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from django.core.cache import cache

logger = logging.getLogger(__name__)


class WikipediaService:
    """
    Service for fetching destination information from Wikipedia.
    
    100% free, no API key required, no rate limits.
    Legal to use with attribution.
    """
    
    BASE_URL = "https://en.wikipedia.org/api/rest_v1"
    
    @classmethod
    def get_destination_summary(cls, destination_name: str) -> Optional[Dict[str, Any]]:
        """
        Get destination summary from Wikipedia.
        
        Args:
            destination_name (str): Name of destination
            
        Returns:
            dict: Summary data or None if not found
        """
        cache_key = f'wiki_summary_{destination_name}'
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            # Search for page
            search_url = f"https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': destination_name,
                'format': 'json',
                'srlimit': 1
            }
            headers = {
                'User-Agent': 'SafariSmart Kenya/1.0 (https://safarismart.co.ke; contact@safarismart.co.ke)'
            }
            
            response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('query', {}).get('search'):
                logger.warning(f"No Wikipedia page found for: {destination_name}")
                return None
                
            page_title = data['query']['search'][0]['title']
            
            # Get page summary
            summary_url = f"{cls.BASE_URL}/page/summary/{page_title}"
            headers = {
                'User-Agent': 'SafariSmart Kenya/1.0 (https://safarismart.co.ke; contact@safarismart.co.ke)'
            }
            response = requests.get(summary_url, headers=headers, timeout=10)
            response.raise_for_status()
            summary_data = response.json()
            
            result = {
                'title': summary_data.get('title'),
                'extract': summary_data.get('extract'),
                'description': summary_data.get('description'),
                'thumbnail': summary_data.get('thumbnail', {}).get('source'),
                'url': summary_data.get('content_urls', {}).get('desktop', {}).get('page'),
                'coordinates': summary_data.get('coordinates'),
            }
            
            # Cache for 7 days
            cache.set(cache_key, result, 60 * 60 * 24 * 7)
            
            logger.info(f"Successfully fetched Wikipedia data for: {destination_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia data for {destination_name}: {str(e)}")
            return None
    
    @classmethod
    def get_destination_images(cls, destination_name: str, limit: int = 5) -> List[str]:
        """
        Get images for destination from Wikipedia.
        
        Args:
            destination_name (str): Name of destination
            limit (int): Maximum number of images
            
        Returns:
            list: List of image URLs
        """
        try:
            # Search for page
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'query',
                'list': 'search',
                'srsearch': destination_name,
                'format': 'json',
                'srlimit': 1
            }
            
            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('query', {}).get('search'):
                return []
                
            page_title = data['query']['search'][0]['title']
            
            # Get page images
            images_url = "https://en.wikipedia.org/w/api.php"
            images_params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'images',
                'format': 'json',
                'imlimit': limit
            }
            
            response = requests.get(images_url, params=images_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            images = []
            
            for page_id, page_data in pages.items():
                if 'images' in page_data:
                    for img in page_data['images']:
                        if img['title'].lower().endswith(('.jpg', '.jpeg', '.png')):
                            images.append(img['title'])
            
            return images[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching Wikipedia images for {destination_name}: {str(e)}")
            return []


class OpenTripMapService:
    """
    Service for fetching tourist attractions from OpenTripMap.
    
    Free tier: 1000 requests/day
    No API key required for basic use
    """
    
    BASE_URL = "https://api.opentripmap.com/0.1/en/places"
    
    @classmethod
    def search_attractions(
        cls,
        latitude: float,
        longitude: float,
        radius: int = 5000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for tourist attractions near coordinates.
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
            radius (int): Search radius in meters (default 5km)
            limit (int): Maximum results
            
        Returns:
            list: List of attractions
        """
        cache_key = f'attractions_{latitude}_{longitude}_{radius}'
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            url = f"{cls.BASE_URL}/radius"
            params = {
                'radius': radius,
                'lon': longitude,
                'lat': latitude,
                'limit': limit,
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            attractions = []
            for item in data:
                attraction = {
                    'name': item.get('name'),
                    'kinds': item.get('kinds', '').split(','),
                    'xid': item.get('xid'),
                    'coordinates': {
                        'lat': item.get('point', {}).get('lat'),
                        'lon': item.get('point', {}).get('lon')
                    }
                }
                attractions.append(attraction)
            
            # Cache for 7 days
            cache.set(cache_key, attractions, 60 * 60 * 24 * 7)
            
            logger.info(f"Found {len(attractions)} attractions near ({latitude}, {longitude})")
            return attractions
            
        except Exception as e:
            logger.error(f"Error fetching OpenTripMap data: {str(e)}")
            return []
    
    @classmethod
    def get_attraction_details(cls, xid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an attraction.
        
        Args:
            xid (str): OpenTripMap attraction ID
            
        Returns:
            dict: Attraction details or None
        """
        cache_key = f'attraction_{xid}'
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            url = f"{cls.BASE_URL}/xid/{xid}"
            params = {'format': 'json'}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            details = {
                'name': data.get('name'),
                'description': data.get('wikipedia_extracts', {}).get('text'),
                'kinds': data.get('kinds', '').split(','),
                'wikipedia': data.get('wikipedia'),
                'image': data.get('preview', {}).get('source'),
                'coordinates': {
                    'lat': data.get('point', {}).get('lat'),
                    'lon': data.get('point', {}).get('lon')
                }
            }
            
            # Cache for 7 days
            cache.set(cache_key, details, 60 * 60 * 24 * 7)
            
            return details
            
        except Exception as e:
            logger.error(f"Error fetching attraction details for {xid}: {str(e)}")
            return None


class NominatimService:
    """
    Service for geocoding using OpenStreetMap Nominatim.
    
    100% free, no API key required
    Please respect usage policy (1 request/second)
    """
    
    BASE_URL = "https://nominatim.openstreetmap.org"
    
    @classmethod
    def geocode(cls, location_name: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates for a location name.
        
        Args:
            location_name (str): Location name
            
        Returns:
            dict: Location data with coordinates or None
        """
        cache_key = f'geocode_{location_name}'
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        try:
            url = f"{cls.BASE_URL}/search"
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1
            }
            headers = {
                'User-Agent': 'SafariSmart Kenya/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                logger.warning(f"No geocoding results for: {location_name}")
                return None
            
            result = {
                'name': data[0].get('display_name'),
                'latitude': float(data[0].get('lat')),
                'longitude': float(data[0].get('lon')),
                'type': data[0].get('type'),
                'importance': data[0].get('importance')
            }
            
            # Cache for 30 days (coordinates don't change)
            cache.set(cache_key, result, 60 * 60 * 24 * 30)
            
            logger.info(f"Geocoded {location_name}: ({result['latitude']}, {result['longitude']})")
            return result
            
        except Exception as e:
            logger.error(f"Error geocoding {location_name}: {str(e)}")
            return None
    
    @classmethod
    def reverse_geocode(cls, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get location name from coordinates.
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude
            
        Returns:
            dict: Location data or None
        """
        try:
            url = f"{cls.BASE_URL}/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json'
            }
            headers = {
                'User-Agent': 'SafariSmart Kenya/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {
                'name': data.get('display_name'),
                'address': data.get('address'),
                'type': data.get('type')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {str(e)}")
            return None


class DestinationEnrichmentService:
    """
    Main service for enriching destination data.
    
    Combines data from multiple free APIs to enhance destination information.
    """
    
    @classmethod
    def enrich_destination(cls, destination_name: str, latitude: float = None, longitude: float = None) -> Dict[str, Any]:
        """
        Enrich destination with data from multiple sources.
        
        Args:
            destination_name (str): Name of destination
            latitude (float, optional): Latitude if known
            longitude (float, optional): Longitude if known
            
        Returns:
            dict: Enriched destination data
        """
        enriched_data = {
            'name': destination_name,
            'wikipedia': None,
            'attractions': [],
            'coordinates': None,
            'images': []
        }
        
        # Get Wikipedia data
        wiki_data = WikipediaService.get_destination_summary(destination_name)
        if wiki_data:
            enriched_data['wikipedia'] = wiki_data
            enriched_data['images'] = [wiki_data.get('thumbnail')] if wiki_data.get('thumbnail') else []
            
            # Get coordinates from Wikipedia if not provided
            if not latitude or not longitude:
                if wiki_data.get('coordinates'):
                    latitude = wiki_data['coordinates'].get('lat')
                    longitude = wiki_data['coordinates'].get('lon')
        
        # If still no coordinates, try geocoding
        if not latitude or not longitude:
            geo_data = NominatimService.geocode(destination_name)
            if geo_data:
                latitude = geo_data['latitude']
                longitude = geo_data['longitude']
                enriched_data['coordinates'] = geo_data
        
        # Get nearby attractions if we have coordinates
        # Note: OpenTripMap requires API key - disabled for now
        # if latitude and longitude:
        #     attractions = OpenTripMapService.search_attractions(latitude, longitude)
        #     enriched_data['attractions'] = attractions
        if latitude and longitude:
            enriched_data['coordinates'] = {
                'latitude': latitude,
                'longitude': longitude
            }
        
        logger.info(f"Enriched destination: {destination_name}")
        return enriched_data
    
    @classmethod
    def enrich_all_destinations(cls):
        """
        Enrich all destinations in database.
        
        This is a management command that can be run periodically.
        """
        from destinations.models import Destination
        
        destinations = Destination.objects.all()
        enriched_count = 0
        
        for dest in destinations:
            try:
                enriched_data = cls.enrich_destination(
                    dest.name,
                    float(dest.latitude) if dest.latitude else None,
                    float(dest.longitude) if dest.longitude else None
                )
                
                # Update destination with enriched data
                if enriched_data.get('wikipedia'):
                    wiki = enriched_data['wikipedia']
                    if wiki.get('extract') and not dest.description:
                        dest.description = wiki['extract']
                    if wiki.get('thumbnail') and not dest.image_url:
                        dest.image_url = wiki['thumbnail']
                
                # Update coordinates if missing
                if enriched_data.get('coordinates') and not dest.latitude:
                    coords = enriched_data['coordinates']
                    dest.latitude = coords.get('latitude')
                    dest.longitude = coords.get('longitude')
                
                dest.save()
                enriched_count += 1
                
                logger.info(f"Enriched: {dest.name}")
                
            except Exception as e:
                logger.error(f"Error enriching {dest.name}: {str(e)}")
                continue
        
        logger.info(f"Enriched {enriched_count}/{destinations.count()} destinations")
        return enriched_count
