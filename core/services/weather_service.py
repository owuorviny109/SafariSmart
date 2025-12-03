"""
Module: services/weather_service.py
Purpose: Service layer for weather data integration

This module contains service classes for fetching and processing weather
data from OpenWeatherMap API.

Classes:
    WeatherService: Main service for weather operations
    WeatherAPIClient: Handles API communication
    WeatherDataParser: Parses API responses
    WeatherCacheManager: Manages weather data caching
 
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import requests
from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)


class WeatherAPIException(Exception):
    """Exception raised when weather API calls fail."""
    pass


# Mapping of destination names to nearest major cities for weather data
DESTINATION_CITY_MAPPING = {
    # Safari destinations
    'Maasai Mara National Reserve': 'Narok',
    'Amboseli National Park': 'Kajiado',
    'Tsavo East National Park': 'Voi',
    'Tsavo West National Park': 'Voi',
    'Tsavo National Park': 'Voi',
    'Lake Nakuru National Park': 'Nakuru',
    'Samburu National Reserve': 'Isiolo',
    'Aberdare National Park': 'Nyeri',
    'Hell\'s Gate National Park': 'Naivasha',
    'Nairobi National Park': 'Nairobi',
    'Meru National Park': 'Meru',
    'Ol Pejeta Conservancy': 'Nanyuki',
    
    # Beach destinations
    'Diani Beach': 'Mombasa',
    'Watamu': 'Malindi',
    'Lamu Island': 'Lamu',
    'Malindi': 'Malindi',
    
    # Mountain destinations
    'Mount Kenya': 'Nanyuki',
    
    # City destinations
    'Nairobi': 'Nairobi',
    'Nairobi City': 'Nairobi',
    'Mombasa': 'Mombasa',
    'Kisumu': 'Kisumu',
    'Nakuru': 'Nakuru',
    
    # Lakes and nature
    'Lake Naivasha': 'Naivasha',
    
    # Cultural destinations
    'Lamu Old Town': 'Lamu',
    'Gede Ruins': 'Malindi',
    'Karen Blixen Museum': 'Nairobi',
    'Giraffe Centre': 'Nairobi',
}


class WeatherAPIClient:
    """
    Client for OpenWeatherMap API communication.
    
    This class handles all HTTP communication with the OpenWeatherMap API,
    including request formatting and error handling.
    
    Attributes:
        api_key (str): OpenWeatherMap API key
        base_url (str): Base URL for API endpoints
        timeout (int): Request timeout in seconds
        
    Example:
        >>> client = WeatherAPIClient()
        >>> data = client.fetch_current_weather("Nairobi", "Kenya")
        >>> print(data['main']['temp'])
        22.5
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    DEFAULT_TIMEOUT = 10
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize weather API client.
        
        Args:
            api_key (str, optional): API key, defaults to settings
            timeout (int): Request timeout in seconds
            
        Raises:
            WeatherAPIException: If API key is missing
        """
        self.api_key = api_key or self._get_api_key_from_settings()
        self.timeout = timeout
        self._validate_api_key()
        
    def _get_api_key_from_settings(self) -> str:
        """
        Get API key from Django settings.
        
        Returns:
            str: OpenWeatherMap API key
        """
        return getattr(settings, 'OPENWEATHER_API_KEY', '')
        
    def _validate_api_key(self) -> None:
        """
        Validate API key is present.
        
        Raises:
            WeatherAPIException: If API key is missing
        """
        if not self.api_key:
            raise WeatherAPIException(
                "OpenWeatherMap API key not configured. "
                "Add OPENWEATHER_API_KEY to .env file."
            )
            
    def fetch_current_weather(
        self,
        city: str,
        country: str = "Kenya"
    ) -> Dict:
        """
        Fetch current weather for a city.
        
        Args:
            city (str): City name
            country (str): Country name (default: Kenya)
            
        Returns:
            Dict: Weather data from API
            
        Raises:
            WeatherAPIException: If API call fails
            
        Example:
            >>> data = client.fetch_current_weather("Nairobi")
            >>> print(data['main']['temp'])
            22.5
        """
        url = f"{self.BASE_URL}/weather"
        params = {
            'q': f'{city},{country}',
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        
        try:
            logger.info(f"Fetching weather for {city}, {country}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Weather data fetched successfully for {city}")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Weather API timeout for {city}")
            raise WeatherAPIException(f"Weather API timeout for {city}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error for {city}: {e}")
            raise WeatherAPIException(f"Failed to fetch weather: {e}")
            
    def fetch_forecast(
        self,
        city: str,
        country: str = "Kenya",
        days: int = 5
    ) -> Dict:
        """
        Fetch weather forecast for a city.
        
        Args:
            city (str): City name
            country (str): Country name (default: Kenya)
            days (int): Number of days (max 5 for free tier)
            
        Returns:
            Dict: Forecast data from API
            
        Raises:
            WeatherAPIException: If API call fails
            
        Example:
            >>> data = client.fetch_forecast("Mombasa", days=3)
            >>> print(len(data['list']))
            24  # 3 days × 8 (3-hour intervals)
        """
        if days > 5:
            logger.warning(f"Requested {days} days, limiting to 5 (free tier)")
            days = 5
            
        url = f"{self.BASE_URL}/forecast"
        params = {
            'q': f'{city},{country}',
            'appid': self.api_key,
            'units': 'metric',
            'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        try:
            logger.info(f"Fetching {days}-day forecast for {city}")
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Forecast data fetched successfully for {city}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast API error for {city}: {e}")
            raise WeatherAPIException(f"Failed to fetch forecast: {e}")


class WeatherDataParser:
    """
    Parser for OpenWeatherMap API responses.
    
    This class extracts and formats relevant weather information
    from API responses into a simplified structure.
    
    Attributes:
        None
        
    Example:
        >>> parser = WeatherDataParser()
        >>> weather = parser.parse_current_weather(api_data)
        >>> print(weather['temperature'])
        22.5
    """
    
    def parse_current_weather(self, data: Dict) -> Dict[str, any]:
        """
        Parse current weather data from API response.
        
        Extracts key weather information and formats it for display.
        
        Args:
            data (Dict): Raw API response
            
        Returns:
            Dict[str, any]: Parsed weather data
            
        Example:
            >>> weather = parser.parse_current_weather(api_data)
            >>> weather['temperature']
            22.5
        """
        try:
            parsed = {
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'], 1),
                'city': data['name']
            }
            
            logger.debug(f"Parsed weather data for {parsed['city']}")
            return parsed
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse weather data: {e}")
            raise WeatherAPIException(f"Invalid weather data format: {e}")
            
    def parse_forecast(self, data: Dict) -> List[Dict[str, any]]:
        """
        Parse forecast data from API response.
        
        Extracts daily forecast information.
        
        Args:
            data (Dict): Raw API response
            
        Returns:
            List[Dict[str, any]]: List of daily forecasts
            
        Example:
            >>> forecasts = parser.parse_forecast(api_data)
            >>> len(forecasts)
            5
        """
        try:
            forecasts = []
            
            # Group by day
            daily_data = {}
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                
                if date not in daily_data:
                    daily_data[date] = []
                daily_data[date].append(item)
                
            # Get average for each day
            for date, items in daily_data.items():
                temps = [item['main']['temp'] for item in items]
                
                forecast = {
                    'date': date.strftime('%Y-%m-%d'),
                    'day_name': date.strftime('%A'),
                    'temp_min': round(min(temps), 1),
                    'temp_max': round(max(temps), 1),
                    'temp_avg': round(sum(temps) / len(temps), 1),
                    'description': items[0]['weather'][0]['description'].title(),
                    'icon': items[0]['weather'][0]['icon']
                }
                forecasts.append(forecast)
                
            logger.debug(f"Parsed {len(forecasts)} daily forecasts")
            return forecasts
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse forecast data: {e}")
            raise WeatherAPIException(f"Invalid forecast data format: {e}")


class WeatherCacheManager:
    """
    Manager for caching weather data.
    
    This class handles caching of weather data to reduce API calls
    and improve performance.
    
    Attributes:
        cache_timeout (int): Cache timeout in seconds
        
    Example:
        >>> cache_mgr = WeatherCacheManager()
        >>> cache_mgr.set_weather("Nairobi", weather_data)
        >>> cached = cache_mgr.get_weather("Nairobi")
    """
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self, cache_timeout: int = CACHE_TIMEOUT):
        """
        Initialize cache manager.
        
        Args:
            cache_timeout (int): Cache timeout in seconds
        """
        self.cache_timeout = cache_timeout
        
    def get_weather(self, city: str) -> Optional[Dict]:
        """
        Get cached weather data for a city.
        
        Args:
            city (str): City name
            
        Returns:
            Optional[Dict]: Cached weather data or None
        """
        cache_key = self._make_cache_key(city, 'current')
        data = cache.get(cache_key)
        
        if data:
            logger.debug(f"Cache hit for {city} weather")
        else:
            logger.debug(f"Cache miss for {city} weather")
            
        return data
        
    def set_weather(self, city: str, data: Dict) -> None:
        """
        Cache weather data for a city.
        
        Args:
            city (str): City name
            data (Dict): Weather data to cache
        """
        cache_key = self._make_cache_key(city, 'current')
        cache.set(cache_key, data, self.cache_timeout)
        logger.debug(f"Cached weather data for {city}")
        
    def get_forecast(self, city: str) -> Optional[List[Dict]]:
        """
        Get cached forecast data for a city.
        
        Args:
            city (str): City name
            
        Returns:
            Optional[List[Dict]]: Cached forecast data or None
        """
        cache_key = self._make_cache_key(city, 'forecast')
        return cache.get(cache_key)
        
    def set_forecast(self, city: str, data: List[Dict]) -> None:
        """
        Cache forecast data for a city.
        
        Args:
            city (str): City name
            data (List[Dict]): Forecast data to cache
        """
        cache_key = self._make_cache_key(city, 'forecast')
        cache.set(cache_key, data, self.cache_timeout)
        logger.debug(f"Cached forecast data for {city}")
        
    def _make_cache_key(self, city: str, data_type: str) -> str:
        """
        Generate cache key for weather data.
        
        Args:
            city (str): City name
            data_type (str): Type of data (current/forecast)
            
        Returns:
            str: Cache key
        """
        return f"weather_{data_type}_{city.lower().replace(' ', '_')}"


class WeatherService:
    """
    Main service for weather operations.
    
    This service orchestrates weather data fetching, parsing, and caching.
    
    Attributes:
        api_client (WeatherAPIClient): API client
        parser (WeatherDataParser): Data parser
        cache_manager (WeatherCacheManager): Cache manager
        
    Example:
        >>> service = WeatherService()
        >>> weather = service.get_current_weather("Nairobi")
        >>> print(weather['temperature'])
        22.5
    """
    
    def __init__(
        self,
        api_client: Optional[WeatherAPIClient] = None,
        parser: Optional[WeatherDataParser] = None,
        cache_manager: Optional[WeatherCacheManager] = None
    ):
        """
        Initialize weather service with dependencies.
        
        Args:
            api_client (WeatherAPIClient, optional): API client
            parser (WeatherDataParser, optional): Data parser
            cache_manager (WeatherCacheManager, optional): Cache manager
        """
        self.api_client = api_client or WeatherAPIClient()
        self.parser = parser or WeatherDataParser()
        self.cache_manager = cache_manager or WeatherCacheManager()
        
    def get_current_weather(
        self,
        city: str,
        use_cache: bool = True
    ) -> Dict[str, any]:
        """
        Get current weather for a city.
        
        Fetches weather data with caching support to reduce API calls.
        
        Args:
            city (str): City name
            use_cache (bool): Whether to use cached data
            
        Returns:
            Dict[str, any]: Current weather data
            
        Raises:
            WeatherAPIException: If weather fetch fails
            
        Example:
            >>> weather = service.get_current_weather("Mombasa")
            >>> print(f"{weather['temperature']}°C")
            28.5°C
        """
        # Try cache first
        if use_cache:
            cached = self.cache_manager.get_weather(city)
            if cached:
                return cached
                
        # Fetch from API
        try:
            raw_data = self.api_client.fetch_current_weather(city)
            parsed_data = self.parser.parse_current_weather(raw_data)
            
            # Cache the result
            if use_cache:
                self.cache_manager.set_weather(city, parsed_data)
                
            return parsed_data
            
        except WeatherAPIException as e:
            logger.error(f"Failed to get weather for {city}: {e}")
            raise
            
    def get_forecast(
        self,
        city: str,
        days: int = 5,
        use_cache: bool = True
    ) -> List[Dict[str, any]]:
        """
        Get weather forecast for a city.
        
        Args:
            city (str): City name
            days (int): Number of days (max 5)
            use_cache (bool): Whether to use cached data
            
        Returns:
            List[Dict[str, any]]: Daily forecast data
            
        Raises:
            WeatherAPIException: If forecast fetch fails
            
        Example:
            >>> forecast = service.get_forecast("Nairobi", days=3)
            >>> for day in forecast:
            ...     print(f"{day['day_name']}: {day['temp_avg']}°C")
        """
        # Try cache first
        if use_cache:
            cached = self.cache_manager.get_forecast(city)
            if cached:
                return cached[:days]
                
        # Fetch from API
        try:
            raw_data = self.api_client.fetch_forecast(city, days=days)
            parsed_data = self.parser.parse_forecast(raw_data)
            
            # Cache the result
            if use_cache:
                self.cache_manager.set_forecast(city, parsed_data)
                
            return parsed_data[:days]
            
        except WeatherAPIException as e:
            logger.error(f"Failed to get forecast for {city}: {e}")
            raise
            
    def get_weather_for_destinations(
        self,
        destinations: List[str]
    ) -> Dict[str, Dict]:
        """
        Get weather for multiple destinations.
        
        Fetches weather data for a list of destinations efficiently.
        Maps destination names to nearest cities for accurate weather data.
        
        Args:
            destinations (List[str]): List of destination names
            
        Returns:
            Dict[str, Dict]: Weather data keyed by destination name
            
        Example:
            >>> destinations = ["Maasai Mara National Reserve", "Diani Beach"]
            >>> weather_data = service.get_weather_for_destinations(destinations)
            >>> print(weather_data["Maasai Mara National Reserve"]["temperature"])
            22.5
        """
        weather_data = {}
        
        for destination in destinations:
            try:
                # Map destination to nearest city
                city = self._map_destination_to_city(destination)
                
                # Fetch weather for the city
                weather = self.get_current_weather(city)
                
                # Store with original destination name as key
                weather_data[destination] = weather
                
            except WeatherAPIException as e:
                logger.warning(f"Skipping weather for {destination}: {e}")
                # Continue with other destinations
                
        logger.info(f"Fetched weather for {len(weather_data)}/{len(destinations)} destinations")
        return weather_data
    
    def _map_destination_to_city(self, destination: str) -> str:
        """
        Map a destination name to the nearest city for weather data.
        
        Args:
            destination (str): Destination name
            
        Returns:
            str: City name for weather lookup
            
        Example:
            >>> city = service._map_destination_to_city("Maasai Mara National Reserve")
            >>> print(city)
            Narok
        """
        # Check if destination is in mapping
        if destination in DESTINATION_CITY_MAPPING:
            city = DESTINATION_CITY_MAPPING[destination]
            logger.debug(f"Mapped '{destination}' to '{city}'")
            return city
        
        # If not in mapping, try to use destination name directly
        # (works for cities like Nairobi, Mombasa, etc.)
        logger.debug(f"No mapping found for '{destination}', using as-is")
        return destination
