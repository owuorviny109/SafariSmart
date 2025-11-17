"""
Management command to enrich destinations with free API data.

Usage:
    python manage.py enrich_destinations
    python manage.py enrich_destinations --destination "Maasai Mara"
"""

from django.core.management.base import BaseCommand
from core.services.destination_enrichment import DestinationEnrichmentService
from destinations.models import Destination


class Command(BaseCommand):
    help = 'Enrich destinations with data from free APIs (Wikipedia, OpenTripMap)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--destination',
            type=str,
            help='Enrich specific destination by name',
        )

    def handle(self, *args, **options):
        destination_name = options.get('destination')

        if destination_name:
            # Enrich specific destination
            try:
                dest = Destination.objects.get(name__icontains=destination_name)
                self.stdout.write(f'Enriching: {dest.name}...')
                
                enriched_data = DestinationEnrichmentService.enrich_destination(
                    dest.name,
                    float(dest.latitude) if dest.latitude else None,
                    float(dest.longitude) if dest.longitude else None
                )
                
                # Update destination
                if enriched_data.get('wikipedia'):
                    wiki = enriched_data['wikipedia']
                    if wiki.get('extract'):
                        dest.description = wiki['extract']
                        self.stdout.write(self.style.SUCCESS(f'  Updated description'))
                    if wiki.get('thumbnail'):
                        dest.image_url = wiki['thumbnail']
                        self.stdout.write(self.style.SUCCESS(f'  Updated image URL'))
                
                if enriched_data.get('coordinates') and not dest.latitude:
                    coords = enriched_data['coordinates']
                    dest.latitude = coords.get('latitude')
                    dest.longitude = coords.get('longitude')
                    self.stdout.write(self.style.SUCCESS(f'  Updated coordinates'))
                
                dest.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully enriched: {dest.name}'))
                
            except Destination.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Destination not found: {destination_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        else:
            # Enrich all destinations
            self.stdout.write('Enriching all destinations...')
            count = DestinationEnrichmentService.enrich_all_destinations()
            self.stdout.write(self.style.SUCCESS(f'Successfully enriched {count} destinations'))
