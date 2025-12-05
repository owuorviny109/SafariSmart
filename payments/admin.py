from django.contrib import admin
from .models import PaymentTransaction, PaymentConfiguration

@admin.register(PaymentConfiguration)
class PaymentConfigurationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enable_mpesa', 'enable_flutterwave', 'enable_sponsorship', 'mpesa_environment')
    fieldsets = (
        ('Feature Toggles', {
            'fields': ('enable_mpesa', 'enable_flutterwave', 'enable_sponsorship', 'enable_subscriptions')
        }),
        ('Environment', {
            'fields': ('mpesa_environment', 'min_transaction_amount')
        }),
        ('Sponsorship Settings', {
            'fields': ('sponsorship_options',),
            'description': 'Enter preset amounts as a list, e.g., [100, 500, 1000]'
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount', 'status', 'transaction_type', 'created_at')
    list_filter = ('status', 'transaction_type', 'created_at')
    search_fields = ('transaction_id', 'phone_number', 'checkout_request_id', 'reference')
    readonly_fields = ('created_at', 'updated_at', 'checkout_request_id', 'merchant_request_id', 'result_code', 'result_desc')
    
    def has_add_permission(self, request):
        return False  # Transactions should be created by the system
