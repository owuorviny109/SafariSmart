from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json


@require_POST
def save_wizard_step(request):
    """Save wizard step data to session"""
    try:
        data = json.loads(request.body)
        step = data.get('step')
        
        # Save to session
        if not request.session.get('wizard_data'):
            request.session['wizard_data'] = {}
        
        request.session['wizard_data'][f'step_{step}'] = data
        request.session.modified = True
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def generate_itinerary(request):
    """Generate itinerary using Gemini AI"""
    try:
        wizard_data = request.session.get('wizard_data', {})
        
        # TODO: Implement Gemini AI generation
        # For now, return placeholder
        
        return JsonResponse({
            'success': True,
            'itinerary_id': 'placeholder',
            'message': 'Itinerary generation coming soon!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
