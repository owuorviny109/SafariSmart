from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.sponsorship_page, name='index'), # Redirect root to sponsorship for now
    path('sponsorship/', views.sponsorship_page, name='sponsorship'),
    path('initiate/', views.initiate_payment, name='initiate'),
    path('callback/', views.mpesa_callback, name='callback'),
    path('status/<str:checkout_request_id>/', views.check_status, name='status'),
]
