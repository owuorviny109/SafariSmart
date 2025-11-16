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


def wizard_step_3(request):
    """Step 3: Travel group"""
    return render(request, 'core/wizard_step_3.html', {'step': 3})


def wizard_step_4(request):
    """Step 4: Budget"""
    return render(request, 'core/wizard_step_4.html', {'step': 4})


def wizard_step_5(request):
    """Step 5: Interests"""
    return render(request, 'core/wizard_step_5.html', {'step': 5})


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
