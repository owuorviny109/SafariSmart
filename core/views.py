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

from typing import Dict, Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView

from .models import WizardSession, Itinerary
from .services import WizardService
from destinations.models import Destination


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
        Process selected destinations.
        
        Validates selections, saves to session, and redirects to step 2.
        
        Args:
            request (HttpRequest): HTTP request object with POST data
            
        Returns:
            HttpResponse: Redirect to step 2 or error response
        """
        wizard_service = WizardService(request.session)
        
        # Get selected destination IDs from POST data
        destination_ids = request.POST.getlist('destinations')
        
        # Convert to integers
        try:
            destination_ids = [int(id) for id in destination_ids]
        except (ValueError, TypeError):
            return self._render_error(
                request,
                "Invalid destination selection. Please try again."
            )
            
        # Validate and save using service
        try:
            wizard_service.save_destinations(destination_ids)
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
        destinations = Destination.objects.all().order_by('destination_type', 'name')
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
        wizard_service = WizardService(request.session)
        
        # Get data from POST
        adults_str = request.POST.get('adults_count', '2')
        children_str = request.POST.get('children_count', '0')
        travel_type = request.POST.get('travel_type', '')
        
        # Convert to integers
        try:
            adults_count = int(adults_str)
            children_count = int(children_str)
        except (ValueError, TypeError):
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
        except ValueError as e:
            return self._render_error(request, wizard_service, str(e))
            
        # Redirect to budget selection
        return redirect('core:budget_selection')
        
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


def wizard_generating(request):
    """Loading screen while AI generates itinerary"""
    return render(request, 'core/wizard_generating.html')


def itinerary_detail(request, share_code):
    """View generated itinerary"""
    itinerary = get_object_or_404(Itinerary, share_code=share_code)
    itinerary.increment_view_count()
    return render(request, 'core/itinerary_detail.html', {
        'itinerary': itinerary
    })


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
