from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Wizard flow
    path('wizard/step-1/', views.wizard_step_1, name='wizard_step_1'),
    path('wizard/step-2/', views.wizard_step_2, name='wizard_step_2'),
    path('wizard/step-3/', views.wizard_step_3, name='wizard_step_3'),
    path('wizard/step-4/', views.wizard_step_4, name='wizard_step_4'),
    path('wizard/step-5/', views.wizard_step_5, name='wizard_step_5'),
    path('wizard/generating/', views.wizard_generating, name='wizard_generating'),
    
    # Itinerary
    path('itinerary/<uuid:share_code>/', views.itinerary_detail, name='itinerary_detail'),
    path('trip/<uuid:share_code>/', views.shared_itinerary, name='shared_itinerary'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
