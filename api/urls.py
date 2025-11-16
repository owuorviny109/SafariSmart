from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('wizard/save-step/', views.save_wizard_step, name='save_wizard_step'),
    path('generate-itinerary/', views.generate_itinerary, name='generate_itinerary'),
]
