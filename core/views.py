"""
Module: core/views.py
Purpose: View layer for core application

This module contains view classes and functions for the core application.
All views follow Django best practices and OOP principles.

Classes:
    WizardStep1View: Handles destination selection (Step 1)
    
Functions:
    landing_page: Landing page view
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

import logging
from typing import Dict, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.conf import settings

from .models import WizardSession, Itinerary
from .services import WizardService, ItineraryGeneratorFactory
from .services.chat_service import TripPlannerChatService, ChatContext
from destinations.models import Destination

logger = logging.getLogger(__name__)


def landing_page(request: HttpRequest) -> HttpResponse:
    """
    Landing page with hero and featured destinations.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        HttpResponse: Rendered landing page
    """
    featured_destinations = Destination.objects.filter(is_featured=True)[:6]
    return render(request, 'core/landing.html', {
        'featured_destinations': featured_destinations
    })


def sitemap(request: HttpRequest) -> HttpResponse:
    """
    Generate XML sitemap for search engines.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        HttpResponse: XML sitemap
    """
    from datetime import datetime
    
    destinations = Destination.objects.all()
    context = {
        'destinations': destinations,
        'current_date': datetime.now()
    }
    
    return render(request, 'sitemap.xml', context, content_type='application/xml')


def robots_txt(request: HttpRequest) -> HttpResponse:
    """
    Generate robots.txt for search engine crawlers.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        HttpResponse: robots.txt file
    """
    return render(request, 'robots.txt', {}, content_type='text/plain')


class DestinationSelectionView(View):
    """
    Handles destination selection for trip planning wizard.
    
    This view manages the first step of the wizard where users select
    destinations they want to visit. Implements multi-select functionality
    with filtering and validation.
    
    Attributes:
        template_name (str): Path to template file
        
    Methods:
        get: Display destination selection interface
        post: Process and validate selected destinations
        
    Example:
        URL: /wizard/destinations/
        GET: Renders destination grid with filters
        POST: Validates selections and advances to duration step
    """
    
    template_name = 'core/destination_selection.html'
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display destination selection page.
        
        Shows all destinations grouped by type with filter options.
        Pre-selects destinations if user is returning to this step.
        
        Args:
            request (HttpRequest): HTTP request object
            
        Returns:
            HttpResponse: Rendered template with destinations
        """
        # Initialize wizard service
        wizard_service = WizardService(request.session)
        
        # Get all destinations ordered by type
        destinations = Destination.objects.all().order_by('destination_type', 'name')
        
        # Get previously selected destinations if any
        selected_destinations = wizard_service.get_selected_destinations()
        selected_ids = [dest.id for dest in selected_destinations]
        
        # Group destinations by type for better UI
        destinations_by_type = self._group_destinations_by_type(destinations)
        
        context = {
            'destinations': destinations,
            'destinations_by_type': destinations_by_type,
            'selected_ids': selected_ids,
            'step': 1,
            'total_steps': 5,
            'progress_percentage': 20,
        }
        
        return render(request, self.template_name, context)
        
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Process selected destinations including custom ones.
        
        Validates selections, saves to session, and redirects to step 2.
        
        Args:
            request (HttpRequest): HTTP request object with POST data
            
        Returns:
            HttpResponse: Redirect to step 2 or error response
        """
        wizard_service = WizardService(request.session)
        
        # Get selected destination IDs from POST data
        destination_ids = request.POST.getlist('destinations')
        
        # Get custom destinations
        import json
        custom_destinations_json = request.POST.get('custom_destinations', '[]')
        try:
            custom_destinations = json.loads(custom_destinations_json)
        except json.JSONDecodeError:
            custom_destinations = []
        
        # Validate at least one destination selected
        if not destination_ids and not custom_destinations:
            return self._render_error(
                request,
                "Please select at least one destination or add a custom one."
            )
        
        # Convert IDs to integers
        try:
            destination_ids = [int(id) for id in destination_ids]
        except (ValueError, TypeError):
            return self._render_error(
                request,
                "Invalid destination selection. Please try again."
            )
            
        # Validate and save using service
        try:
            wizard_service.save_destinations(destination_ids, custom_destinations)
        except ValueError as e:
            return self._render_error(request, str(e))
            
        # Redirect to duration selection
        return redirect('core:duration_selection')
        
    def _group_destinations_by_type(
        self,
        destinations: Any
    ) -> Dict[str, list]:
        """
        Group destinations by their type.
        
        Args:
            destinations: QuerySet of Destination objects
            
        Returns:
            Dict[str, list]: Destinations grouped by type
            
        Example:
            {
                'safari': [dest1, dest2],
                'beach': [dest3, dest4],
                ...
            }
        """
        grouped = {}
        
        for destination in destinations:
            dest_type = destination.destination_type
            if dest_type not in grouped:
                grouped[dest_type] = []
            grouped[dest_type].append(destination)
            
        return grouped
        
    def _render_error(
        self,
        request: HttpRequest,
        error_message: str
    ) -> HttpResponse:
        """
        Render page with error message.
        
        Args:
            request (HttpRequest): HTTP request object
            error_message (str): Error message to display
            
        Returns:
            HttpResponse: Rendered template with error
        """
        destinations = Destination.objects.filter(is_featured=True).order_by('destination_type', 'name')
        destinations_by_type = self._group_destinations_by_type(destinations)
        
        context = {
            'destinations': destinations,
            'destinations_by_type': destinations_by_type,
            'selected_ids': [],
            'step': 1,
            'total_steps': 5,
            'progress_percentage': 20,
            'error_message': error_message,
        }
        
        return render(request, self.template_name, context)


class DurationSelectionView(View):
    """
    Handles trip duration and date selection for wizard.
    
    This view manages duration selection with predefined options
    and optional date range specification. Validates date logic
    and duration constraints.
    
    Attributes:
        template_name (str): Path to template file
        DURATION_OPTIONS (list): Available duration choices
        
    Methods:
        get: Display duration selection interface
        post: Process and validate duration and dates
        
    Example:
        URL: /wizard/duration/
        GET: Renders duration options and date picker
        POST: Validates inputs and advances to travel group step
    """
    
    template_name = 'core/duration_selection.html'
    
    # Duration options (in days)
    DURATION_OPTIONS = [
        {'value': 1, 'label': '1 Day', 'description': 'Quick day trip'},
        {'value': 3, 'label': '2-3 Days', 'description': 'Weekend getaway'},
        {'value': 5, 'label': '4-5 Days', 'description': 'Short vacation'},
        {'value': 7, 'label': '1 Week', 'description': 'Full week adventure'},
        {'value': 14, 'label': '2 Weeks', 'description': 'Extended safari'},
    ]
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display duration selection page.
        
        Shows duration options and date picker. Pre-fills if user
        is returning to this step.
        
        Args:
            request (HttpRequest): HTTP request object
            
        Returns:
            HttpResponse: Rendered template with duration options
        """
        wizard_service = WizardService(request.session)
        
        # Get previously selected duration if any
        duration_data = wizard_service.get_duration_data()
        selected_duration = duration_data.get('duration_days')
        start_date = duration_data.get('start_date', '')
        end_date = duration_data.get('end_date', '')
        
        # Get selected destinations for context
        destinations = wizard_service.get_selected_destinations()
        
        context = {
            'duration_options': self.DURATION_OPTIONS,
            'selected_duration': selected_duration,
            'start_date': start_date,
            'end_date': end_date,
            'destinations': destinations,
            'destination_count': len(destinations),
            'step': 2,
            'total_steps': 5,
            'progress_percentage': 40,
        }
        
        return render(request, self.template_name, context)
        
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Process duration and dates.
        
        Validates inputs, saves to session, and redirects to step 3.
        
        Args:
            request (HttpRequest): HTTP request object with POST data
            
        Returns:
            HttpResponse: Redirect to step 3 or error response
        """
        wizard_service = WizardService(request.session)
        
        # Get duration from POST data
        duration_str = request.POST.get('duration')
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()
        
        # Convert duration to integer
        try:
            duration_days = int(duration_str)
        except (ValueError, TypeError):
            return self._render_error(
                request,
                wizard_service,
                "Please select a valid duration"
            )
            
        # Validate and save using service
        try:
            wizard_service.save_duration(
                duration_days,
                start_date if start_date else None,
                end_date if end_date else None
            )
        except ValueError as e:
            return self._render_error(request, wizard_service, str(e))
            
        # Redirect to travel group selection
        return redirect('core:travel_group_selection')
        
    def _render_error(
        self,
        request: HttpRequest,
        wizard_service: WizardService,
        error_message: str
    ) -> HttpResponse:
        """
        Render page with error message.
        
        Args:
            request (HttpRequest): HTTP request object
            wizard_service (WizardService): Wizard service instance
            error_message (str): Error message to display
            
        Returns:
            HttpResponse: Rendered template with error
        """
        destinations = wizard_service.get_selected_destinations()
        
        context = {
            'duration_options': self.DURATION_OPTIONS,
            'selected_duration': None,
            'start_date': '',
            'end_date': '',
            'destinations': destinations,
            'destination_count': len(destinations),
            'step': 2,
            'total_steps': 5,
            'progress_percentage': 40,
            'error_message': error_message,
        }
        
        return render(request, self.template_name, context)


class TravelGroupSelectionView(View):
    """
    Handles travel group composition selection for wizard.
    
    This view manages the selection of group size (adults/children)
    and travel type (solo, family, couple, friends). Implements
    counter controls and validation.
    
    Attributes:
        template_name (str): Path to template file
        TRAVEL_TYPES (list): Available travel type options
        
    Methods:
        get: Display travel group selection interface
        post: Process and validate group composition
        
    Example:
        URL: /wizard/travel-group/
        GET: Renders counters and travel type buttons
        POST: Validates inputs and advances to budget step
    """
    
    template_name = 'core/travel_group_selection.html'
    
    # Travel type options
    TRAVEL_TYPES = [
        {
            'value': 'solo',
            'label': 'Solo Traveler',
            'icon': 'person',
            'description': 'Traveling alone'
        },
        {
            'value': 'couple',
            'label': 'Couple',
            'icon': 'heart',
            'description': 'Romantic getaway'
        },
        {
            'value': 'family',
            'label': 'Family',
            'icon': 'people',
            'description': 'Family vacation'
        },
        {
            'value': 'friends',
            'label': 'Friends',
            'icon': 'emoji-smile',
            'description': 'Group of friends'
        },
    ]
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display travel group selection page.
        
        Shows counters for adults/children and travel type buttons.
        Pre-fills if user is returning to this step.
        
        Args:
            request (HttpRequest): HTTP request object
            
        Returns:
            HttpResponse: Rendered template with group options
        """
        wizard_service = WizardService(request.session)
        
        # Get previously selected data if any
        group_data = wizard_service.get_travel_group_data()
        adults_count = group_data.get('adults_count', 2)
        children_count = group_data.get('children_count', 0)
        selected_type = group_data.get('travel_type')
        
        # Get previous step data for context
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        
        context = {
            'travel_types': self.TRAVEL_TYPES,
            'adults_count': adults_count,
            'children_count': children_count,
            'selected_type': selected_type,
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'step': 3,
            'total_steps': 5,
            'progress_percentage': 60,
        }
        
        return render(request, self.template_name, context)
        
    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Process travel group selection.
        
        Validates group composition, saves to session, and redirects to step 4.
        
        Args:
            request (HttpRequest): HTTP request object with POST data
            
        Returns:
            HttpResponse: Redirect to step 4 or error response
        """
        logger = logging.getLogger(__name__)
        
        try:
            wizard_service = WizardService(request.session)
            
            # Get data from POST
            adults_str = request.POST.get('adults_count', '2')
            children_str = request.POST.get('children_count', '0')
            travel_type = request.POST.get('travel_type', '')
            
            logger.info(f"Travel group POST: adults={adults_str}, children={children_str}, type={travel_type}")
            
            # Convert to integers
            try:
                adults_count = int(adults_str)
                children_count = int(children_str)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid traveler count: {e}")
                return self._render_error(
                    request,
                    wizard_service,
                    "Invalid number of travelers"
                )
                
            # Validate and save using service
            try:
                wizard_service.save_travel_group(
                    adults_count,
                    children_count,
                    travel_type
                )
                logger.info("Travel group data saved successfully")
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                return self._render_error(request, wizard_service, str(e))
                
            # Redirect to budget selection
            return redirect('core:budget_selection')
            
        except Exception as e:
            logger.exception(f"Unexpected error in travel group POST: {e}")
            return JsonResponse({
                'error': 'An unexpected error occurred. Please try again.',
                'details': str(e) if settings.DEBUG else None
            }, status=500)
        
    def _render_error(
        self,
        request: HttpRequest,
        wizard_service: WizardService,
        error_message: str
    ) -> HttpResponse:
        """
        Render page with error message.
        
        Args:
            request (HttpRequest): HTTP request object
            wizard_service (WizardService): Wizard service instance
            error_message (str): Error message to display
            
        Returns:
            HttpResponse: Rendered template with error
        """
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        
        context = {
            'travel_types': self.TRAVEL_TYPES,
            'adults_count': 2,
            'children_count': 0,
            'selected_type': None,
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'step': 3,
            'total_steps': 5,
            'progress_percentage': 60,
            'error_message': error_message,
        }
        
        return render(request, self.template_name, context)


class BudgetSelectionView(View):
    """
    Handles budget selection for wizard.

    This view manages budget amount selection via slider and
    budget category selection (budget, mid-range, luxury).
    Calculates per-person costs.

    Attributes:
        template_name (str): Path to template file
        BUDGET_CATEGORIES (list): Available budget categories

    Methods:
        get: Display budget selection interface
        post: Process and validate budget

    Example:
        URL: /wizard/budget/
        GET: Renders slider and category buttons
        POST: Validates inputs and advances to interests step
    """

    template_name = 'core/budget_selection.html'

    # Budget categories
    BUDGET_CATEGORIES = [
        {
            'value': 'budget',
            'label': 'Budget',
            'icon': 'piggy-bank',
            'description': 'Affordable options',
            'range': 'KSh 10k - 50k'
        },
        {
            'value': 'mid-range',
            'label': 'Mid-Range',
            'icon': 'wallet2',
            'description': 'Comfortable travel',
            'range': 'KSh 50k - 150k'
        },
        {
            'value': 'luxury',
            'label': 'Luxury',
            'icon': 'gem',
            'description': 'Premium experience',
            'range': 'KSh 150k+'
        },
    ]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display budget selection page.

        Shows budget slider and category buttons. Pre-fills if user
        is returning to this step.

        Args:
            request (HttpRequest): HTTP request object

        Returns:
            HttpResponse: Rendered template with budget options
        """
        wizard_service = WizardService(request.session)

        # Get previously selected data if any
        budget_data = wizard_service.get_budget_data()
        budget_amount = budget_data.get('budget_amount', 100000)
        selected_category = budget_data.get('budget_category')

        # Get previous step data for context
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        group_data = wizard_service.get_travel_group_data()

        # Calculate per person budget
        total_travelers = group_data.get('total_travelers', 1)
        per_person_budget = budget_amount // total_travelers

        context = {
            'budget_categories': self.BUDGET_CATEGORIES,
            'budget_amount': budget_amount,
            'selected_category': selected_category,
            'per_person_budget': per_person_budget,
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'total_travelers': total_travelers,
            'step': 4,
            'total_steps': 5,
            'progress_percentage': 80,
        }

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Process budget selection.

        Validates budget, saves to session, and redirects to step 5.

        Args:
            request (HttpRequest): HTTP request object with POST data

        Returns:
            HttpResponse: Redirect to step 5 or error response
        """
        wizard_service = WizardService(request.session)

        # Get data from POST
        budget_str = request.POST.get('budget_amount', '100000')
        budget_category = request.POST.get('budget_category', '')

        # Convert to integer
        try:
            budget_amount = int(budget_str)
        except (ValueError, TypeError):
            return self._render_error(
                request,
                wizard_service,
                "Invalid budget amount"
            )

        # Validate and save using service
        try:
            wizard_service.save_budget(budget_amount, budget_category)
        except ValueError as e:
            return self._render_error(request, wizard_service, str(e))

        # Redirect to interests selection
        return redirect('core:interests_selection')

    def _render_error(
        self,
        request: HttpRequest,
        wizard_service: WizardService,
        error_message: str
    ) -> HttpResponse:
        """
        Render page with error message.

        Args:
            request (HttpRequest): HTTP request object
            wizard_service (WizardService): Wizard service instance
            error_message (str): Error message to display

        Returns:
            HttpResponse: Rendered template with error
        """
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        group_data = wizard_service.get_travel_group_data()

        context = {
            'budget_categories': self.BUDGET_CATEGORIES,
            'budget_amount': 100000,
            'selected_category': None,
            'per_person_budget': 100000 // group_data.get('total_travelers', 1),
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'total_travelers': group_data.get('total_travelers', 1),
            'step': 4,
            'total_steps': 5,
            'progress_percentage': 80,
            'error_message': error_message,
        }

        return render(request, self.template_name, context)


class InterestsSelectionView(View):
    """
    Handles interests selection for wizard (final step).

    This view manages the selection of user interests to personalize
    the itinerary. Multi-select with visual cards.

    Attributes:
        template_name (str): Path to template file
        INTERESTS (list): Available interest options

    Methods:
        get: Display interests selection interface
        post: Process selections and complete wizard

    Example:
        URL: /wizard/interests/
        GET: Renders interest cards
        POST: Validates and redirects to generation
    """

    template_name = 'core/interests_selection.html'

    # Interest options
    INTERESTS = [
        {
            'value': 'wildlife',
            'label': 'Wildlife',
            'icon': 'binoculars-fill',
            'description': 'Safari & animals'
        },
        {
            'value': 'culture',
            'label': 'Culture',
            'icon': 'people-fill',
            'description': 'Local traditions'
        },
        {
            'value': 'food',
            'label': 'Food',
            'icon': 'cup-hot-fill',
            'description': 'Culinary experiences'
        },
        {
            'value': 'adventure',
            'label': 'Adventure',
            'icon': 'lightning-fill',
            'description': 'Thrilling activities'
        },
        {
            'value': 'relaxation',
            'label': 'Relaxation',
            'icon': 'sun-fill',
            'description': 'Rest & unwind'
        },
        {
            'value': 'photography',
            'label': 'Photography',
            'icon': 'camera-fill',
            'description': 'Scenic views'
        },
        {
            'value': 'history',
            'label': 'History',
            'icon': 'book-fill',
            'description': 'Historical sites'
        },
        {
            'value': 'nature',
            'label': 'Nature',
            'icon': 'tree-fill',
            'description': 'Natural beauty'
        },
        {
            'value': 'beach',
            'label': 'Beach',
            'icon': 'umbrella-fill',
            'description': 'Coastal activities'
        },
        {
            'value': 'nightlife',
            'label': 'Nightlife',
            'icon': 'moon-stars-fill',
            'description': 'Evening entertainment'
        },
    ]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display interests selection page.

        Shows interest cards for multi-select. Pre-fills if user
        is returning to this step.

        Args:
            request (HttpRequest): HTTP request object

        Returns:
            HttpResponse: Rendered template with interest options
        """
        wizard_service = WizardService(request.session)

        # Get previously selected interests if any
        interests_data = wizard_service.get_interests_data()
        selected_interests = interests_data.get('interests', [])

        # Get all previous step data for summary
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        group_data = wizard_service.get_travel_group_data()
        budget_data = wizard_service.get_budget_data()

        context = {
            'interests': self.INTERESTS,
            'selected_interests': selected_interests,
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'total_travelers': group_data.get('total_travelers', 1),
            'budget_amount': budget_data.get('budget_amount', 0),
            'step': 5,
            'total_steps': 5,
            'progress_percentage': 100,
        }

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Process interests selection and complete wizard.

        Validates selections, saves to session, and redirects to
        itinerary generation.

        Args:
            request (HttpRequest): HTTP request object with POST data

        Returns:
            HttpResponse: Redirect to generation or error response
        """
        wizard_service = WizardService(request.session)

        # Get selected interests from POST data
        interests = request.POST.getlist('interests')

        # Validate and save using service
        try:
            wizard_service.save_interests(interests)
        except ValueError as e:
            return self._render_error(request, wizard_service, str(e))

        # Redirect to itinerary generation
        return redirect('core:itinerary_generation')

    def _render_error(
        self,
        request: HttpRequest,
        wizard_service: WizardService,
        error_message: str
    ) -> HttpResponse:
        """
        Render page with error message.

        Args:
            request (HttpRequest): HTTP request object
            wizard_service (WizardService): Wizard service instance
            error_message (str): Error message to display

        Returns:
            HttpResponse: Rendered template with error
        """
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        group_data = wizard_service.get_travel_group_data()
        budget_data = wizard_service.get_budget_data()

        context = {
            'interests': self.INTERESTS,
            'selected_interests': [],
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'total_travelers': group_data.get('total_travelers', 1),
            'budget_amount': budget_data.get('budget_amount', 0),
            'step': 5,
            'total_steps': 5,
            'progress_percentage': 100,
            'error_message': error_message,
        }

        return render(request, self.template_name, context)


class ItineraryGenerationView(View):
    """
    Displays loading screen while AI generates itinerary.

    This view shows animated loading messages while the itinerary
    is being generated in the background. Uses AJAX to poll for
    completion status.

    Attributes:
        template_name (str): Path to template file

    Methods:
        get: Display loading screen with wizard summary

    Example:
        URL: /wizard/generating/
        GET: Shows loading animation
        Redirects to itinerary when complete
    """

    template_name = 'core/itinerary_generation.html'

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Display itinerary generation loading screen.

        Shows all wizard selections and animated loading messages.

        Args:
            request (HttpRequest): HTTP request object

        Returns:
            HttpResponse: Rendered loading template
        """
        wizard_service = WizardService(request.session)

        # Get all wizard data for display
        destinations = wizard_service.get_selected_destinations()
        duration_data = wizard_service.get_duration_data()
        group_data = wizard_service.get_travel_group_data()
        budget_data = wizard_service.get_budget_data()
        interests_data = wizard_service.get_interests_data()

        # Check if wizard is completed
        if not wizard_service.session_manager.is_completed():
            # Redirect back to start if wizard not completed
            return redirect('core:destination_selection')

        context = {
            'destinations': destinations,
            'duration_days': duration_data.get('duration_days'),
            'start_date': duration_data.get('start_date'),
            'total_travelers': group_data.get('total_travelers', 1),
            'travel_type': group_data.get('travel_type'),
            'budget_amount': budget_data.get('budget_amount', 0),
            'budget_category': budget_data.get('budget_category'),
            'interests': interests_data.get('interests', []),
        }

        return render(request, self.template_name, context)


def itinerary_detail(request: HttpRequest, share_code: str) -> HttpResponse:
    """
    Display itinerary detail page.
    
    This view handles the display of a generated itinerary using
    service classes for data preparation and formatting.
    
    Args:
        request (HttpRequest): HTTP request object
        share_code (str): Unique share code for itinerary
        
    Returns:
        HttpResponse: Rendered itinerary detail page
        
    Example:
        URL: /itinerary/abc-123-def-456/
        Displays: Full itinerary with route visualization
    """
    from core.services import ItineraryDisplayService, ShareService
    
    # Get itinerary
    itinerary = get_object_or_404(Itinerary, share_code=share_code)
    
    # Increment view count
    itinerary.increment_view_count()
    
    # Prepare display data using service
    display_service = ItineraryDisplayService()
    display_data = display_service.prepare_display_data(itinerary)
    
    # Prepare share data using service
    share_service = ShareService()
    share_data = share_service.prepare_share_data(itinerary)
    
    # Build context
    context = {
        **display_data,
        'share_data': share_data,
        'is_authenticated': request.user.is_authenticated,
        'login_url': f"/login/?next={request.path}"
    }
    
    logger.info(f"Displaying itinerary {itinerary.id} (views: {itinerary.view_count})")
    
    return render(request, 'core/itinerary_detail_new.html', context)


def shared_itinerary(request, share_code):
    """Public shared itinerary view"""
    return itinerary_detail(request, share_code)


@login_required
def dashboard(request):
    """User dashboard with saved itineraries"""
    itineraries = Itinerary.objects.filter(user=request.user, is_saved=True)
    return render(request, 'core/dashboard.html', {
        'itineraries': itineraries
    })


def quick_trip(request: HttpRequest) -> HttpResponse:
    """
    Quick trip planner - parse natural language input and generate itinerary.
    
    Accepts input like: "2 days trip to Kakamega with 20000 budget"
    Parses it and generates itinerary directly.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        HttpResponse: Redirect to generated itinerary or error
    """
    if request.method != 'POST':
        return redirect('core:landing')
    
    trip_description = request.POST.get('trip_description', '').strip()
    
    if not trip_description:
        logger.warning("Quick trip: Empty description")
        return redirect('core:landing')
    
    # Validate input
    from core.services.quick_trip_parser import QuickTripParser, QuickTripValidationError
    
    try:
        from datetime import datetime, timedelta
        from django.contrib import messages
        from core.services.abuse_detector import AbuseDetector
        
        now = datetime.now().timestamp()
        
        # Initialize abuse detector
        abuse_detector = AbuseDetector()
        ip_address = abuse_detector.get_client_ip(request)
        session_key = request.session.session_key or 'anonymous'
        
        # Check if IP is blocked (severe abuse)
        is_blocked, block_reason, remaining_seconds = abuse_detector.is_blocked(ip_address, session_key)
        if is_blocked:
            logger.warning(f"Blocked IP {ip_address} attempted quick trip")
            messages.error(request, f"{block_reason} Please use the step-by-step planner.")
            return redirect('core:destination_selection')
        
        # Session-level tracking (lighter abuse)
        invalid_attempts = request.session.get('quick_trip_invalid_attempts', [])
        # Remove old entries (older than 10 minutes)
        invalid_attempts = [ts for ts in invalid_attempts if now - ts < 600]
        
        # Check for session-level abuse (10 invalid attempts in 10 minutes)
        if len(invalid_attempts) >= 10:
            logger.warning(f"Quick trip session abuse detected for {session_key}")
            # Temporarily block session for 30 minutes
            block_until = request.session.get('quick_trip_blocked_until', 0)
            if now < block_until:
                remaining_minutes = int((block_until - now) / 60)
                messages.error(
                    request,
                    f"Too many invalid attempts. Try again in {remaining_minutes} minutes or use the step-by-step planner."
                )
                return redirect('core:destination_selection')
            else:
                # Set new block
                request.session['quick_trip_blocked_until'] = now + 1800  # 30 minutes
                messages.error(
                    request,
                    "Too many invalid attempts. Quick trip feature is temporarily disabled for 30 minutes. "
                    "Please use the step-by-step planner."
                )
                return redirect('core:destination_selection')
        
        # Check if session is currently blocked
        block_until = request.session.get('quick_trip_blocked_until', 0)
        if now < block_until:
            remaining_minutes = int((block_until - now) / 60)
            messages.error(
                request,
                f"Quick trip feature is temporarily disabled. Try again in {remaining_minutes} minutes or use the step-by-step planner."
            )
            return redirect('core:destination_selection')
        
        # Validate before parsing
        parser = QuickTripParser()
        validation_error = parser.validate_input(trip_description)
        
        if validation_error:
            logger.warning(f"Quick trip validation failed from IP {ip_address}: {validation_error}")
            
            # Track invalid attempt (both session and IP)
            invalid_attempts.append(now)
            request.session['quick_trip_invalid_attempts'] = invalid_attempts
            abuse_detector.track_invalid_attempt(ip_address, session_key)
            
            # Get IP-level attempt count
            ip_attempt_count = abuse_detector.get_invalid_attempt_count(ip_address)
            
            # Show progressive warnings
            if ip_attempt_count >= 40:
                messages.error(
                    request,
                    f"{validation_error} (WARNING: {ip_attempt_count}/50 attempts - continued abuse will result in 24-hour block)"
                )
            elif len(invalid_attempts) >= 7:
                messages.warning(
                    request,
                    f"{validation_error} ({len(invalid_attempts)}/10 attempts - feature will be temporarily disabled after 10 invalid attempts)"
                )
            else:
                messages.error(request, validation_error)
            
            return redirect('core:landing')
        
        # Rate limiting - max 5 successful quick trips per session per hour
        quick_trips = request.session.get('quick_trips', [])
        # Remove old entries (older than 1 hour)
        quick_trips = [ts for ts in quick_trips if now - ts < 3600]
        
        if len(quick_trips) >= 5:
            logger.warning(f"Quick trip rate limit exceeded for session {session_key}")
            messages.warning(
                request, 
                "You've reached the limit of 5 quick trips per hour. Please use the step-by-step planner or try again later."
            )
            return redirect('core:destination_selection')
        
        # Clear invalid attempts on successful validation
        request.session['quick_trip_invalid_attempts'] = []
        abuse_detector.clear_attempts(ip_address, session_key)
        
        # Add to rate limit tracker
        quick_trips.append(now)
        request.session['quick_trips'] = quick_trips
        
        # Parse the natural language input
        trip_data = parser.parse(trip_description)
        
        # Generate itinerary using parsed data
        itinerary_data = ItineraryGeneratorFactory.generate_with_fallback(trip_data)
        
        # Save to database
        itinerary = Itinerary.objects.create(
            user=request.user if request.user.is_authenticated else None,
            title=itinerary_data['title'],
            duration_days=itinerary_data['duration_days'],
            adults_count=trip_data.get('adults_count', 2),
            children_count=trip_data.get('children_count', 0),
            travel_type=trip_data.get('travel_type', 'friends'),
            total_budget=itinerary_data['budget_amount'],
            budget_category=trip_data.get('budget_category', 'mid-range'),
            itinerary_data={'content': itinerary_data['content'], 'generated_by': itinerary_data['generated_by']},
            cost_breakdown={},
            is_saved=request.user.is_authenticated
        )
        
        # Add destinations if any were parsed
        if trip_data.get('destinations'):
            for dest in trip_data['destinations']:
                itinerary.destinations.add(dest)
        
        logger.info(f"Quick trip generated: {itinerary.share_code}")
        
        # Redirect to itinerary
        return redirect('core:itinerary_detail', share_code=itinerary.share_code)
        
    except Exception as e:
        logger.error(f"Quick trip generation failed: {e}")
        # Fall back to wizard
        return redirect('core:destination_selection')


def generate_itinerary_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to generate itinerary using AI.
    
    This endpoint processes wizard data and generates an itinerary
    using Gemini AI with automatic fallback to template generator.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        JsonResponse: Generated itinerary data or error
        
    Example:
        POST /api/generate-itinerary/
        Returns: {
            'status': 'success',
            'itinerary': {...},
            'share_code': 'abc123'
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST method required'
        }, status=405)
        
    try:
        wizard_service = WizardService(request.session)
        
        # Verify wizard is completed
        if not wizard_service.session_manager.is_completed():
            return JsonResponse({
                'status': 'error',
                'message': 'Wizard not completed'
            }, status=400)
            
        # Gather all wizard data
        preferences = {
            'destinations': wizard_service.get_selected_destinations(),
            'custom_destinations': wizard_service.get_custom_destinations(),
            'duration_days': wizard_service.get_duration_data().get('duration_days'),
            'start_date': wizard_service.get_duration_data().get('start_date'),
            'budget_amount': wizard_service.get_budget_data().get('budget_amount'),
            'budget_category': wizard_service.get_budget_data().get('budget_category'),
            'adults_count': wizard_service.get_travel_group_data().get('adults_count'),
            'children_count': wizard_service.get_travel_group_data().get('children_count'),
            'travel_type': wizard_service.get_travel_group_data().get('travel_type'),
            'interests': wizard_service.get_interests_data().get('interests', []),
        }
        
        # Log generation start
        logger.info(f"Starting itinerary generation for {len(preferences['destinations'])} destinations, {preferences['duration_days']} days")
        
        # Generate itinerary with AI (automatic fallback to template)
        try:
            itinerary_data = ItineraryGeneratorFactory.generate_with_fallback(preferences)
            logger.info(f"Itinerary generated successfully using {itinerary_data.get('generated_by', 'unknown')}")
        except Exception as gen_error:
            logger.error(f"Generation error: {str(gen_error)}")
            raise
        
        # Save to database
        itinerary = Itinerary.objects.create(
            user=request.user if request.user.is_authenticated else None,
            title=itinerary_data['title'],
            duration_days=itinerary_data['duration_days'],
            adults_count=preferences['adults_count'],
            children_count=preferences['children_count'],
            travel_type=preferences['travel_type'],
            total_budget=itinerary_data['budget_amount'],
            budget_category=preferences['budget_category'],
            itinerary_data={'content': itinerary_data['content'], 'generated_by': itinerary_data['generated_by']},
            cost_breakdown={},  # Can be populated later
            is_saved=request.user.is_authenticated
        )
        
        # Add destinations
        for dest in preferences['destinations']:
            itinerary.destinations.add(dest)
            
        logger.info(
            f"Generated itinerary {itinerary.share_code} "
            f"using {itinerary_data['generated_by']}"
        )
        
        return JsonResponse({
            'status': 'success',
            'itinerary': {
                'id': itinerary.id,
                'title': itinerary.title,
                'share_code': str(itinerary.share_code),
                'generated_by': itinerary_data['generated_by']
            },
            'redirect_url': f'/itinerary/{itinerary.share_code}/'
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Itinerary generation failed: {str(e)}\n{error_details}")
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to generate itinerary: {str(e)}',
            'debug': error_details if settings.DEBUG else None
        }, status=500)



# ============================================
# CHAT API VIEWS
# ============================================

def chat_start_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to start a new chat conversation.
    
    Initializes chat service and returns welcome message.
    
    Args:
        request (HttpRequest): HTTP request object
        
    Returns:
        JsonResponse: Welcome message and session info
        
    Example:
        POST /api/chat/start/
        Returns: {
            'status': 'success',
            'message': 'Hi! I'm your Safari planning assistant...',
            'session_id': 'abc123'
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST method required'
        }, status=405)
        
    try:
        chat_service = TripPlannerChatService()
        response = chat_service.start_conversation()
        
        # Store context in session
        if not hasattr(request.session, 'chat_context'):
            request.session['chat_context'] = {}
            
        session_id = request.session.session_key or request.session.create()
        
        return JsonResponse({
            'status': 'success',
            'message': response['message'],
            'session_id': session_id,
            'type': response['type']
        })
        
    except Exception as e:
        logger.error(f"Chat start failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to start chat'
        }, status=500)


def chat_message_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to process chat messages.
    
    Handles user messages and returns bot responses with
    extracted trip data.
    
    Args:
        request (HttpRequest): HTTP request object with message
        
    Returns:
        JsonResponse: Bot response and extracted data
        
    Example:
        POST /api/chat/message/
        Body: {'message': 'I want to visit Rongo for 3 days'}
        Returns: {
            'status': 'success',
            'message': 'Great! What's your budget level?',
            'completed': false,
            'extracted_data': {...}
        }
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'POST method required'
        }, status=405)
        
    try:
        import json
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'status': 'error',
                'message': 'Message is required'
            }, status=400)
            
        # Get or create chat context
        # In production, use proper session management
        context = ChatContext()
        
        # Process message
        chat_service = TripPlannerChatService()
        response = chat_service.process_message(user_message, context)
        
        return JsonResponse({
            'status': 'success',
            'message': response['message'],
            'type': response['type'],
            'completed': response['completed'],
            'extracted_data': response.get('extracted_data', {})
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to process message'
        }, status=500)
