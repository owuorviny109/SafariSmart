from django.contrib import admin
from .models import Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination_type', 'county', 'average_cost_per_day', 'is_featured']
    list_filter = ['destination_type', 'is_featured', 'county']
    search_fields = ['name', 'description', 'county']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured']
