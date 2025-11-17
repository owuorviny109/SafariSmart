"""
Script to load initial configuration data.
Run with: python manage.py shell < load_config_data.py
"""

from core.models import (
    TravelType,
    BudgetCategory,
    InterestCategory,
    BudgetEstimate,
    SystemConfiguration
)

print("Loading initial configuration data...")

# Travel Types
travel_types_data = [
    {'code': 'solo', 'name': 'Solo Traveler', 'description': 'Traveling alone for personal adventure and discovery', 'icon': '👤', 'sort_order': 1},
    {'code': 'couple', 'name': 'Couple', 'description': 'Romantic getaway for two', 'icon': '💑', 'sort_order': 2},
    {'code': 'family', 'name': 'Family Trip', 'description': 'Family vacation with children', 'icon': '👨‍👩‍👧‍👦', 'sort_order': 3},
    {'code': 'friends', 'name': 'Friends Group', 'description': 'Adventure with friends', 'icon': '👥', 'sort_order': 4},
]

for data in travel_types_data:
    TravelType.objects.get_or_create(code=data['code'], defaults=data)
    print(f"✓ Created/Updated TravelType: {data['name']}")

# Budget Categories
budget_categories_data = [
    {'code': 'budget', 'name': 'Budget-Friendly', 'description': 'Affordable options for budget-conscious travelers', 'min_budget_per_day': 5000, 'max_budget_per_day': 10000, 'icon': '💰', 'sort_order': 1},
    {'code': 'mid-range', 'name': 'Mid-Range', 'description': 'Comfortable accommodations and quality experiences', 'min_budget_per_day': 10000, 'max_budget_per_day': 25000, 'icon': '💵', 'sort_order': 2},
    {'code': 'luxury', 'name': 'Luxury', 'description': 'Premium accommodations and exclusive experiences', 'min_budget_per_day': 25000, 'max_budget_per_day': 100000, 'icon': '💎', 'sort_order': 3},
]

for data in budget_categories_data:
    BudgetCategory.objects.get_or_create(code=data['code'], defaults=data)
    print(f"✓ Created/Updated BudgetCategory: {data['name']}")

# Budget Estimates
budget_estimates_data = [
    {
        'category_code': 'budget',
        'accommodation_min': 5000, 'accommodation_max': 8000,
        'activities_min': 3000, 'activities_max': 5000,
        'meals_min': 2000, 'meals_max': 3000,
        'transport_min': 2000, 'transport_max': 4000,
        'notes': 'Budget-friendly options with basic accommodations and essential activities'
    },
    {
        'category_code': 'mid-range',
        'accommodation_min': 10000, 'accommodation_max': 15000,
        'activities_min': 5000, 'activities_max': 8000,
        'meals_min': 3000, 'meals_max': 5000,
        'transport_min': 4000, 'transport_max': 6000,
        'notes': 'Mid-range options with comfortable lodges and quality activities'
    },
    {
        'category_code': 'luxury',
        'accommodation_min': 20000, 'accommodation_max': 40000,
        'activities_min': 10000, 'activities_max': 15000,
        'meals_min': 5000, 'meals_max': 8000,
        'transport_min': 6000, 'transport_max': 10000,
        'notes': 'Luxury options with premium resorts and exclusive experiences'
    },
]

for data in budget_estimates_data:
    category = BudgetCategory.objects.get(code=data['category_code'])
    estimate_data = {k: v for k, v in data.items() if k != 'category_code'}
    BudgetEstimate.objects.get_or_create(budget_category=category, defaults=estimate_data)
    print(f"✓ Created/Updated BudgetEstimate for: {category.name}")

# Interest Categories
interest_categories_data = [
    {'code': 'wildlife', 'name': 'Wildlife & Safari', 'description': 'Game drives, animal viewing, and safari experiences', 'icon': '🦁', 'sort_order': 1},
    {'code': 'culture', 'name': 'Culture & Heritage', 'description': 'Local traditions, villages, and cultural experiences', 'icon': '🏛️', 'sort_order': 2},
    {'code': 'food', 'name': 'Food & Cuisine', 'description': 'Local dishes, cooking classes, and culinary experiences', 'icon': '🍽️', 'sort_order': 3},
    {'code': 'adventure', 'name': 'Adventure & Sports', 'description': 'Hiking, climbing, water sports, and adrenaline activities', 'icon': '🏔️', 'sort_order': 4},
    {'code': 'relaxation', 'name': 'Relaxation & Wellness', 'description': 'Spa treatments, yoga, and peaceful retreats', 'icon': '🧘', 'sort_order': 5},
    {'code': 'photography', 'name': 'Photography', 'description': 'Scenic viewpoints, wildlife photography, and photo tours', 'icon': '📸', 'sort_order': 6},
    {'code': 'history', 'name': 'History & Museums', 'description': 'Historical sites, museums, and archaeological locations', 'icon': '📚', 'sort_order': 7},
    {'code': 'nature', 'name': 'Nature & Hiking', 'description': 'Nature walks, bird watching, and eco-tourism', 'icon': '🌿', 'sort_order': 8},
    {'code': 'beach', 'name': 'Beach & Water', 'description': 'Beach activities, snorkeling, diving, and water sports', 'icon': '🏖️', 'sort_order': 9},
    {'code': 'nightlife', 'name': 'Nightlife & Entertainment', 'description': 'Evening entertainment, bars, and local nightlife', 'icon': '🎭', 'sort_order': 10},
]

for data in interest_categories_data:
    InterestCategory.objects.get_or_create(code=data['code'], defaults=data)
    print(f"✓ Created/Updated InterestCategory: {data['name']}")

# System Configuration
config, created = SystemConfiguration.objects.get_or_create(
    pk=1,
    defaults={
        'min_trip_duration': 1,
        'max_trip_duration': 30,
        'min_budget': 10000,
        'max_budget': 500000,
        'min_adults': 1,
        'max_adults': 20,
        'max_children': 20,
        'max_total_travelers': 30,
        'max_destinations': 10,
        'max_interests': 10,
        'enable_ai_generation': True,
        'enable_weather_forecasts': True,
        'enable_custom_destinations': True,
        'support_email': 'info@safarismart.co.ke',
        'updated_by': 'system'
    }
)
print(f"✓ {'Created' if created else 'Updated'} SystemConfiguration")

print("\n✅ All configuration data loaded successfully!")
print(f"   - {TravelType.objects.count()} Travel Types")
print(f"   - {BudgetCategory.objects.count()} Budget Categories")
print(f"   - {BudgetEstimate.objects.count()} Budget Estimates")
print(f"   - {InterestCategory.objects.count()} Interest Categories")
print(f"   - 1 System Configuration")
