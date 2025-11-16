"""
Module: tests/test_itinerary_display_service.py
Purpose: Unit tests for itinerary display service

This module contains comprehensive unit tests for the itinerary
display service classes.

Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from decimal import Decimal
from django.test import TestCase
from unittest.mock import Mock, MagicMock

from core.services.itinerary_display_service import (
    RouteVisualizationService,
    CostBreakdownService,
    ItineraryDisplayService
)
from core.models import Itinerary
from destinations.models import Destination


class TestRouteVisualizationService(TestCase):
    """Unit tests for RouteVisualizationService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = RouteVisualizationService()
        
    def test_generate_route_data_with_valid_destinations(self):
        """Test route generation with valid destinations."""
        # Arrange
        dest1 = Mock(spec=Destination)
        dest1.name = "Maasai Mara"
        dest1.destination_type = "safari"
        dest1.county = "Narok"
        
        dest2 = Mock(spec=Destination)
        dest2.name = "Diani Beach"
        dest2.destination_type = "beach"
        dest2.county = "Kwale"
        
        destinations = [dest1, dest2]
        
        # Act
        result = self.service.generate_route_data(destinations)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "Maasai Mara")
        self.assertEqual(result[0]['type'], "Safari")
        self.assertEqual(result[0]['county'], "Narok")
        self.assertEqual(result[1]['name'], "Diani Beach")
        
    def test_generate_route_data_with_empty_list(self):
        """Test route generation with empty destination list."""
        # Arrange
        destinations = []
        
        # Act
        result = self.service.generate_route_data(destinations)
        
        # Assert
        self.assertEqual(result, [])
        
    def test_get_destination_icon_for_safari(self):
        """Test icon selection for safari destination."""
        # Act
        icon = self.service._get_destination_icon('safari')
        
        # Assert
        self.assertEqual(icon, 'binoculars-fill')
        
    def test_get_destination_icon_for_unknown_type(self):
        """Test icon selection for unknown destination type."""
        # Act
        icon = self.service._get_destination_icon('unknown')
        
        # Assert
        self.assertEqual(icon, 'geo-alt-fill')


class TestCostBreakdownService(TestCase):
    """Unit tests for CostBreakdownService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = CostBreakdownService()
        
    def test_calculate_breakdown_with_existing_data(self):
        """Test breakdown calculation with existing cost data."""
        # Arrange
        itinerary = Mock(spec=Itinerary)
        itinerary.cost_breakdown = {
            'accommodation': 50000,
            'activities': 30000,
            'meals': 15000,
            'transport': 5000
        }
        
        # Act
        result = self.service.calculate_breakdown(itinerary)
        
        # Assert
        self.assertEqual(result['accommodation'], Decimal('50000'))
        self.assertEqual(result['activities'], Decimal('30000'))
        self.assertEqual(len(result), 4)
        
    def test_calculate_breakdown_without_data(self):
        """Test breakdown calculation without existing data."""
        # Arrange
        itinerary = Mock(spec=Itinerary)
        itinerary.cost_breakdown = None
        itinerary.total_budget = 100000
        itinerary.budget_category = 'mid-range'
        
        # Act
        result = self.service.calculate_breakdown(itinerary)
        
        # Assert
        self.assertIn('accommodation', result)
        self.assertIn('activities', result)
        self.assertIsInstance(result['accommodation'], Decimal)
        
    def test_format_breakdown_for_display(self):
        """Test formatting breakdown for display."""
        # Arrange
        breakdown = {
            'accommodation': Decimal('50000'),
            'activities': Decimal('30000')
        }
        
        # Act
        result = self.service.format_breakdown_for_display(breakdown)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], 'Accommodation')
        self.assertIn('KSh', result[0][1])


class TestItineraryDisplayService(TestCase):
    """Unit tests for ItineraryDisplayService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.route_service = Mock(spec=RouteVisualizationService)
        self.cost_service = Mock(spec=CostBreakdownService)
        self.service = ItineraryDisplayService(
            self.route_service,
            self.cost_service
        )
        
    def test_prepare_display_data_with_valid_itinerary(self):
        """Test display data preparation with valid itinerary."""
        # Arrange
        itinerary = Mock(spec=Itinerary)
        itinerary.id = 1
        itinerary.total_budget = 100000
        itinerary.itinerary_data = {
            'content': 'Test content',
            'generated_by': 'gemini-ai'
        }
        
        # Mock destinations
        dest_mock = MagicMock()
        dest_mock.all.return_value = []
        itinerary.destinations = dest_mock
        
        # Mock service responses
        self.route_service.generate_route_data.return_value = []
        self.cost_service.calculate_breakdown.return_value = {}
        self.cost_service.format_breakdown_for_display.return_value = []
        
        # Act
        result = self.service.prepare_display_data(itinerary)
        
        # Assert
        self.assertIn('itinerary', result)
        self.assertIn('route_data', result)
        self.assertIn('cost_breakdown', result)
        self.assertIn('is_ai_generated', result)
        self.assertTrue(result['is_ai_generated'])
        
    def test_prepare_display_data_with_invalid_itinerary(self):
        """Test display data preparation with invalid itinerary."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.service.prepare_display_data(None)
            
    def test_extract_content_from_dict(self):
        """Test content extraction from dictionary."""
        # Arrange
        itinerary = Mock(spec=Itinerary)
        itinerary.itinerary_data = {'content': 'Test content'}
        
        # Act
        result = self.service._extract_content(itinerary)
        
        # Assert
        self.assertEqual(result, 'Test content')
        
    def test_extract_generated_by_from_dict(self):
        """Test generated_by extraction from dictionary."""
        # Arrange
        itinerary = Mock(spec=Itinerary)
        itinerary.itinerary_data = {'generated_by': 'gemini-ai'}
        
        # Act
        result = self.service._extract_generated_by(itinerary)
        
        # Assert
        self.assertEqual(result, 'gemini-ai')
