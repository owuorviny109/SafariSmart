from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import WizardSession, Itinerary
from destinations.models import Destination


def landing_page(request):
    """Landing page with hero and featured destinations"""
    featured_destinations = Destination.objects.filter(is_featured=True)[:6]
    return render(request, 'core/landing.html', {
        'featured_destinations': featured_destinations
    })


def wizard_step_1(request):
    """Step 1: Select destinations"""
    destinations = Destination.objects.all()
    return render(request, 'core/wizard_step_1.html', {
        'destinations': destinations,
        'step': 1
    })


def wizard_step_2(request):
    """Step 2: Duration and dates"""
    return render(request, 'core/wizard_step_2.html', {'step': 2})


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
