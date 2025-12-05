import logging
import requests
import uuid
from django.conf import settings
from django.db import transaction
from .models import PaymentTransaction, PaymentConfiguration

logger = logging.getLogger(__name__)

class FlutterwaveService:
    """
    Service wrapper for Flutterwave interactions.
    Handles Standard Checkout (Redirect) flow.
    """
    
    BASE_URL = "https://api.flutterwave.com/v3"
    
    def __init__(self):
        self.config = PaymentConfiguration.get_config()
        self.secret_key = settings.FLW_SECRET_KEY
        self.public_key = settings.FLW_PUBLIC_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
    def initiate_payment(self, amount, email, phone_number=None, name=None, user=None, description="SafariSmart Payment"):
        """
        Initiates a Standard Payment (Redirect).
        Returns the redirect URL.
        """
        try:
            # 1. Generate unique reference
            tx_ref = f"SS-{uuid.uuid4().hex[:12].upper()}"
            
            # 2. Prepare Payload
            payload = {
                "tx_ref": tx_ref,
                "amount": str(amount),
                "currency": "KES", # Default to KES, can be USD
                "redirect_url": settings.FLW_CALLBACK_URL, # e.g. https://safarismart.co.ke/payments/flutterwave/callback/
                "payment_options": "card,mobilemoney,ussd",
                "customer": {
                    "email": email,
                    "phonenumber": phone_number or "",
                    "name": name or "SafariSmart Guest"
                },
                "customizations": {
                    "title": "SafariSmart Kenya",
                    "description": description,
                    "logo": "https://safarismart.co.ke/static/assets/img/logo.png" # Update with real logo URL
                }
            }
            
            # 3. Create Pending Record
            with transaction.atomic():
                PaymentTransaction.objects.create(
                    checkout_request_id=tx_ref, # Using tx_ref as ID
                    flutterwave_ref=tx_ref,
                    user=user,
                    phone_number=phone_number or "N/A",
                    amount=amount,
                    transaction_type='sponsorship',
                    payment_provider='flutterwave',
                    reference='Sponsorship',
                    description=description,
                    status='pending'
                )
                
                # 4. Call Flutterwave API
                response = requests.post(
                    f"{self.BASE_URL}/payments",
                    json=payload,
                    headers=self.headers
                )
                
                res_data = response.json()
                
                if response.status_code == 200 and res_data.get('status') == 'success':
                    return {
                        'success': True,
                        'redirect_url': res_data['data']['link']
                    }
                else:
                    logger.error(f"Flutterwave Init Failed: {res_data}")
                    return {'success': False, 'error': res_data.get('message', 'Initialization failed')}
                    
        except Exception as e:
            logger.exception("Error initiating Flutterwave payment")
            return {'success': False, 'error': str(e)}

    def verify_transaction(self, tx_ref, transaction_id=None):
        """
        Verifies a transaction status from Flutterwave.
        Can verify by tx_ref or transaction_id (flw_id).
        """
        try:
            # If we have transaction_id (from callback), verify that specific ID
            # Otherwise verify by tx_ref
            
            endpoint = f"{self.BASE_URL}/transactions/verify_by_reference?tx_ref={tx_ref}"
            if transaction_id:
                 endpoint = f"{self.BASE_URL}/transactions/{transaction_id}/verify"
                 
            response = requests.get(endpoint, headers=self.headers)
            res_data = response.json()
            
            if response.status_code == 200 and res_data.get('status') == 'success':
                data = res_data['data']
                
                # Check status and currency/amount match
                flw_status = data.get('status')
                flw_amount = data.get('amount')
                flw_currency = data.get('currency')
                flw_id = data.get('id')
                
                # Update Record
                with transaction.atomic():
                    txn = PaymentTransaction.objects.filter(flutterwave_ref=tx_ref).first()
                    if txn:
                        if flw_status == 'successful' and float(flw_amount) >= float(txn.amount):
                            txn.status = 'completed'
                            txn.transaction_id = str(flw_id)
                            txn.result_desc = "Payment Successful"
                            txn.result_code = 0
                        elif flw_status == 'failed':
                            txn.status = 'failed'
                            txn.result_desc = "Payment Failed at Processor"
                        
                        txn.save()
                        return True, "Verified"
                    else:
                        return False, "Transaction not found"
            else:
                return False, "Verification failed"
                
        except Exception as e:
            logger.exception("Error verifying Flutterwave payment")
            return False, str(e)
