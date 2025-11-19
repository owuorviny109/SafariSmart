"""
Management command to create initial email settings.

Usage: python manage.py setup_email_settings
"""

from django.core.management.base import BaseCommand
from core.models_email import EmailSettings


class Command(BaseCommand):
    help = 'Create initial email settings'
    
    def handle(self, *args, **options):
        try:
            settings = EmailSettings.get_settings()
            
            if settings:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Email settings already exist: {settings.company_name}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        'Email settings created successfully!'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating email settings: {str(e)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\nYou can now configure email settings in Django Admin:\n'
                '1. Go to Django Admin\n'
                '2. Navigate to "Email Settings"\n'
                '3. Configure your business email addresses\n'
                '4. Set company branding information\n'
                '5. Enable/disable email features as needed'
            )
        )