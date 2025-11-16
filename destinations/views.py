from django.shortcuts import render, get_object_or_404
from .models import Destination


def destination_list(request):
    """Browse all destinations"""
    destinations = Destination.objects.all()
    destination_type = request.GET.get('type')
    
    if destination_type:
        destinations = destinations.filter(destination_type=destination_type)
    
    return render(request, 'destinations/list.html', {
        'destinations': destinations,
        'selected_type': destination_type
    })


def destination_detail(request, slug):
    """Destination detail page"""
    destination = get_object_or_404(Destination, slug=slug)
    return render(request, 'destinations/detail.html', {
        'destination': destination
    })
