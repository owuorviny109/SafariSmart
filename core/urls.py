from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # SEO
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots'),
    
    # Static pages (About, Privacy, Terms, etc.)
    path('page/<slug:slug>/', views.static_page, name='static_page'),
    
    # Quick trip planner
    path('quick-trip/', views.quick_trip, name='quick_trip'),
    
    # Wizard flow - descriptive names
    path('wizard/destinations/', views.DestinationSelectionView.as_view(), name='destination_selection'),
    path('wizard/duration/', views.DurationSelectionView.as_view(), name='duration_selection'),
    path('wizard/travel-group/', views.TravelGroupSelectionView.as_view(), name='travel_group_selection'),
    path('wizard/budget/', views.BudgetSelectionView.as_view(), name='budget_selection'),
    path('wizard/interests/', views.InterestsSelectionView.as_view(), name='interests_selection'),
    path('wizard/generating/', views.ItineraryGenerationView.as_view(), name='itinerary_generation'),
    
    # Itinerary
    path('itinerary/<uuid:share_code>/', views.itinerary_detail, name='itinerary_detail'),
    path('itinerary/<uuid:share_code>/save/', views.save_itinerary, name='save_itinerary'),
    path('trip/<uuid:share_code>/', views.shared_itinerary, name='shared_itinerary'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/generate-itinerary/', views.generate_itinerary_api, name='generate_itinerary_api'),
    path('api/chat/start/', views.chat_start_api, name='chat_start'),
    path('api/chat/message/', views.chat_message_api, name='chat_message'),
]
