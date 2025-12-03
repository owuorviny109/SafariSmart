"""
Module: services/__init__.py
Purpose: Service layer package initialization

This package contains service classes that encapsulate business logic
for the SafariSmart Kenya application.

"""

from .wizard_service import WizardService, WizardSessionManager
from .itinerary_generator import (
    GeminiItineraryGenerator,
    TemplateItineraryGenerator,
    ItineraryGeneratorFactory
)
from .itinerary_display_service import (
    ItineraryDisplayService,
    RouteVisualizationService,
    CostBreakdownService
)
from .share_service import (
    ShareService,
    ShareURLGenerator,
    ShareTracker
)
from .analytics_service import (
    DestinationAnalyticsService,
    VisitStatsCalculator,
    TrendingDestinationsService
)
from .weather_service import (
    WeatherService,
    WeatherAPIClient,
    WeatherDataParser
)

__all__ = [
    'WizardService',
    'WizardSessionManager',
    'GeminiItineraryGenerator',
    'TemplateItineraryGenerator',
    'ItineraryGeneratorFactory',
    'ItineraryDisplayService',
    'RouteVisualizationService',
    'CostBreakdownService',
    'ShareService',
    'ShareURLGenerator',
    'ShareTracker',
    'DestinationAnalyticsService',
    'VisitStatsCalculator',
    'TrendingDestinationsService',
    'WeatherService',
    'WeatherAPIClient',
    'WeatherDataParser',
]
