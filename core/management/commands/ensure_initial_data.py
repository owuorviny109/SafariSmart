"""
Management command to ensure initial configuration data is loaded.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import TravelType, BudgetCategory, InterestCategory, SystemConfiguration


class Command(BaseCommand):
    help = 'Ensures initial configuration data is loaded into the database'

    def handle(self, *args, **options):
        """Load initial data if not already present."""
        
        # Check if data already exists
        travel_types_count = TravelType.objects.count()
        budget_categories_count = BudgetCategory.objects.count()
        interest_categories_count = InterestCategory.objects.count()
        
        self.stdout.write(f"Current counts:")
        self.stdout.write(f"  - Travel Types: {travel_types_count}")
        self.stdout.write(f"  - Budget Categories: {budget_categories_count}")
        self.stdout.write(f"  - Interest Categories: {interest_categories_count}")
        
        # Load if missing
        if travel_types_count == 0 or budget_categories_count == 0 or interest_categories_count == 0:
            self.stdout.write(self.style.WARNING('Initial data missing. Loading fixtures...'))
            try:
                call_command('loaddata', 'core/fixtures/initial_configuration.json')
                self.stdout.write(self.style.SUCCESS('✓ Initial configuration loaded successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error loading configuration: {e}'))
                raise
        else:
            self.stdout.write(self.style.SUCCESS('✓ Initial configuration already present'))
        
        # Verify system configuration
        if not SystemConfiguration.objects.exists():
            self.stdout.write(self.style.WARNING('Creating default system configuration...'))
            SystemConfiguration.objects.create(
                min_trip_duration=1,
                max_trip_duration=30,
                min_budget=10000,
                max_budget=500000,
                min_adults=1,
                max_adults=20,
                max_children=20,
                max_total_travelers=30,
                enable_ai_generation=True,
                updated_by='system'
            )
            self.stdout.write(self.style.SUCCESS('✓ System configuration created'))
