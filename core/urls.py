from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Wizard flow - descriptive names
    path('wizard/destinations/', views.DestinationSelectionView.as_view(), name='destination_selection'),
    path('wizard/duration/', views.DurationSelectionView.as_view(), name='duration_selection'),
    path('wizard/travel-group/', views.wizard_step_3, name='travel_group_selection'),
    path('wizard/budget/', views.wizard_step_4, name='budget_selection'),
    path('wizard/interests/', views.wizard_step_5, name='interests_selection'),
    path('wizard/generating/', views.wizard_generating, name='itinerary_generation'),
    
    # Itinerary
    path('itinerary/<uuid:share_code>/', views.itinerary_detail, name='itinerary_detail'),
    path('trip/<uuid:share_code>/', views.shared_itinerary, name='shared_itinerary'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
