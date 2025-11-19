"""
Calculate daily business metrics.

Usage: python manage.py calculate_daily_metrics
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models_privacy_analytics import BusinessMetrics


class Command(BaseCommand):
    help = 'Calculate daily business metrics'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to calculate (default: 1 for yesterday)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        
        for i in range(days):
            date = timezone.now().date() - timedelta(days=i+1)
            
            try:
                metrics = BusinessMetrics.calculate_daily_metrics(date)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Calculated metrics for {date}: '
                        f'{metrics.total_page_views} views, '
                        f'{metrics.unique_sessions} visitors'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error calculating metrics for {date}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Daily metrics calculation complete!'
                f'\nYou can now view your website traffic in Django Admin:'
                f'\n1. Go to Django Admin'
                f'\n2. Navigate to "Anonymous Page Views" to see individual visits'
                f'\n3. Navigate to "Business Metrics" to see daily summaries'
            )
        )