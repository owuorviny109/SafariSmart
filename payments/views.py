import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .services import MPesaService
from .models import PaymentTransaction, PaymentConfiguration

logger = logging.getLogger(__name__)

def sponsorship_page(request):
    """Renders the sponsorship/donation page."""
    config = PaymentConfiguration.get_config()
    
    if not config.enable_sponsorship:
        return render(request, 'payments/disabled.html', {'feature': 'Sponsorship'})
        
    context = {
        'options': config.sponsorship_options,
        'min_amount': config.min_transaction_amount
    }
    return render(request, 'payments/sponsorship.html', context)

@require_POST
def initiate_payment(request):
    """
    API Endpoint to start the payment process.
    Expects JSON: { "phone": "07...", "amount": 100 }
    """
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        amount = data.get('amount')
        
        if not phone or not amount:
            return JsonResponse({'success': False, 'error': 'Phone and Amount are required'})
            
        # Format Phone (Ensure 254...)
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+254'):
            phone = phone[1:]
            
        service = MPesaService()
        result = service.initiate_stk_push(
            phone_number=phone,
            amount=float(amount),
            reference='Sponsorship',
            description='Support SafariSmart',
            user=request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        logger.exception("Payment Initiation Error")
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def mpesa_callback(request):
    """
    Callback URL for Safaricom.
    MUST be csrf_exempt.
    """
    try:
        data = json.loads(request.body)
        logger.info(f"M-Pesa Callback Received: {data}")
        
        service = MPesaService()
        service.handle_callback(data)
        
        # Always return success to Safaricom to stop retries
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
    except Exception as e:
        logger.exception("Callback Error")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Failed'})

@require_GET
def check_status(request, checkout_request_id):
    """
    Poll this endpoint to check if payment is complete.
    """
    try:
        transaction = PaymentTransaction.objects.get(checkout_request_id=checkout_request_id)
        return JsonResponse({
            'status': transaction.status,
            'message': transaction.result_desc
        })
    except PaymentTransaction.DoesNotExist:
        return JsonResponse({'status': 'pending', 'message': 'Transaction not found yet'})
