from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.sponsorship_page, name='index'), # Redirect root to sponsorship for now
    path('sponsorship/', views.sponsorship_page, name='sponsorship'),
    path('initiate/', views.initiate_payment, name='initiate'),
    path('initiate-card/', views.initiate_card_payment, name='initiate_card'),
    path('callback/', views.mpesa_callback, name='callback'),
    path('flutterwave/callback/', views.flutterwave_callback, name='flutterwave_callback'),
    path('status/<str:checkout_request_id>/', views.check_status, name='status'),
]
