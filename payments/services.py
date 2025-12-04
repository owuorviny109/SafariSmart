import logging
import requests
from django.conf import settings
from django.db import transaction
from django_daraja.mpesa.core import MpesaClient
from .models import PaymentTransaction, PaymentConfiguration

logger = logging.getLogger(__name__)

class MPesaService:
    """
    Service wrapper for M-Pesa interactions.
    Adds reliability layers (ACID, Logging) on top of django-daraja.
    """
    
    def __init__(self):
        self.client = MpesaClient()
        self.config = PaymentConfiguration.get_config()
        
    def initiate_stk_push(self, phone_number, amount, reference, description, user=None):
        """
        Initiates an STK Push request.
        
        Args:
            phone_number (str): Format 2547...
            amount (int): Amount to charge
            reference (str): Account Reference (e.g. Order ID)
            description (str): Transaction Description
            user (User, optional): User initiating the payment
            
        Returns:
            dict: Response with success/error details
        """
        # 1. Validate Amount
        if amount < self.config.min_transaction_amount:
            return {'success': False, 'error': f"Minimum amount is KSh {self.config.min_transaction_amount}"}
            
        # 2. Create Pending Transaction Record (Atomic)
        try:
            with transaction.atomic():
                # Call M-Pesa API
                # Note: django-daraja handles the auth and request construction
                response = self.client.stk_push(
                    phone_number, 
                    int(amount), 
                    account_reference=reference, 
                    transaction_desc=description,
                    callback_url=settings.MPESA_CALLBACK_URL
                )
                
                # Parse Response
                # django-daraja returns a JSON response object
                res_data = response.json()
                
                if response.status_code == 200 and 'ResponseCode' in res_data and res_data['ResponseCode'] == '0':
                    # Success from Safaricom
                    checkout_request_id = res_data['CheckoutRequestID']
                    merchant_request_id = res_data['MerchantRequestID']
                    
                    # Create Record
                    PaymentTransaction.objects.create(
                        checkout_request_id=checkout_request_id,
                        merchant_request_id=merchant_request_id,
                        user=user,
                        phone_number=phone_number,
                        amount=amount,
                        transaction_type='sponsorship', # Default for now
                        reference=reference,
                        description=description,
                        status='pending'
                    )
                    
                    return {
                        'success': True, 
                        'message': 'STK Push initiated. Check your phone.',
                        'checkout_request_id': checkout_request_id
                    }
                else:
                    # Error from Safaricom
                    error_msg = res_data.get('errorMessage', 'Unknown error from M-Pesa')
                    logger.error(f"M-Pesa STK Push Failed: {error_msg}")
                    return {'success': False, 'error': error_msg}
                    
        except Exception as e:
            logger.exception("Error initiating STK Push")
            return {'success': False, 'error': str(e)}

    def handle_callback(self, payload):
        """
        Processes the M-Pesa Callback.
        Implements Idempotency and Atomic updates.
        """
        try:
            stk_callback = payload.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            if not checkout_request_id:
                logger.error("Callback missing CheckoutRequestID")
                return False

            # 1. Idempotency Check
            # If already completed, ignore
            transaction_record = PaymentTransaction.objects.filter(checkout_request_id=checkout_request_id).first()
            
            if not transaction_record:
                logger.error(f"Callback received for unknown CheckoutRequestID: {checkout_request_id}")
                return False
                
            if transaction_record.status in ['completed', 'failed']:
                logger.info(f"Duplicate callback for {checkout_request_id}. Ignoring.")
                return True

            # 2. Atomic Update
            with transaction.atomic():
                transaction_record.result_code = result_code
                transaction_record.result_desc = result_desc
                
                if result_code == 0:
                    # SUCCESS
                    transaction_record.status = 'completed'
                    
                    # Extract Metadata (Receipt No, etc.)
                    meta_items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                    for item in meta_items:
                        name = item.get('Name')
                        value = item.get('Value')
                        if name == 'MpesaReceiptNumber':
                            transaction_record.transaction_id = value
                        # Can extract Phone, Amount, Date if needed to verify
                    
                    logger.info(f"Payment Confirmed: {transaction_record.transaction_id}")
                else:
                    # FAILED / CANCELLED
                    transaction_record.status = 'failed'
                    logger.warning(f"Payment Failed: {result_desc}")
                
                transaction_record.save()
                return True
                
        except Exception as e:
            logger.exception("Error processing callback")
            return False
