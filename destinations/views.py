from django.shortcuts import render, get_object_or_404
from .models import Destination
import logging

logger = logging.getLogger(__name__)


def destination_list(request):
    """Browse all destinations with weather data"""
    destinations = Destination.objects.all()
    destination_type = request.GET.get('type')
    
    if destination_type:
        destinations = destinations.filter(destination_type=destination_type)
    
    # Get weather for featured/visible destinations (limit to avoid too many API calls)
    weather_data = {}
    try:
        from core.services.weather_service import WeatherService, WeatherAPIException
        weather_service = WeatherService()
        
        # Get weather for first 6 destinations (or featured ones)
        featured_destinations = list(destinations.filter(is_featured=True)[:6])
        if not featured_destinations:
            featured_destinations = list(destinations[:6])
        
        destination_names = [d.name for d in featured_destinations]
        weather_data = weather_service.get_weather_for_destinations(destination_names)
        
    except (WeatherAPIException, Exception) as e:
        logger.warning(f"Could not fetch weather data: {e}")
        # Continue without weather data
    
    return render(request, 'destinations/list.html', {
        'destinations': destinations,
        'selected_type': destination_type,
        'weather_data': weather_data
    })


def destination_detail(request, slug):
    """Destination detail page with weather forecast"""
    destination = get_object_or_404(Destination, slug=slug)
    
    # Get weather for this destination
    weather_data = None
    forecast_data = None
    
    try:
        from core.services.weather_service import WeatherService, WeatherAPIException
        weather_service = WeatherService()
        
        # Get current weather
        weather_dict = weather_service.get_weather_for_destinations([destination.name])
        weather_data = weather_dict.get(destination.name)
        
        # Get 3-day forecast
        from core.services.weather_service import DESTINATION_CITY_MAPPING
        city = DESTINATION_CITY_MAPPING.get(destination.name, destination.name)
        forecast_data = weather_service.get_forecast(city, days=3)
        
    except (WeatherAPIException, Exception) as e:
        logger.warning(f"Could not fetch weather for {destination.name}: {e}")
        # Continue without weather data
    
    return render(request, 'destinations/detail.html', {
        'destination': destination,
        'weather_data': weather_data,
        'forecast_data': forecast_data
    })
