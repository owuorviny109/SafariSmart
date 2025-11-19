from django.contrib import admin
from .models import WizardSession, Itinerary


@admin.register(WizardSession)
class WizardSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'current_step', 'completed', 'created_at']
    list_filter = ['completed', 'current_step', 'created_at']
    search_fields = ['session_key', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'duration_days', 'total_budget', 'view_count', 'is_saved', 'created_at']
    list_filter = ['is_saved', 'budget_category', 'travel_type', 'created_at']
    search_fields = ['title', 'user__email', 'share_code']
    readonly_fields = ['share_code', 'view_count', 'created_at', 'updated_at']
    filter_horizontal = ['destinations']


# Import and register configuration admin interfaces
from .admin_config import (
    TravelTypeAdmin,
    BudgetCategoryAdmin,
    InterestCategoryAdmin,
    BudgetEstimateAdmin,
    SystemConfigurationAdmin
)

# Import and register security admin interfaces
from .admin_security import (
    SecuritySettingsAdmin,
    SecurityEventAdmin
)

# Import and register static pages admin
from .admin_pages import StaticPageAdmin, ContactInfoAdmin

# Admin interfaces are already registered via @admin.register decorators
