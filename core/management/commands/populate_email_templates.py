"""
Management command to populate initial email templates.
"""

from django.core.management.base import BaseCommand
from core.models_email import EmailTemplate

class Command(BaseCommand):
    help = 'Populate initial email templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Welcome Email',
                'email_type': 'welcome',
                'subject': 'Welcome to {{ site_name }}!',
                'html_content': '''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #198754;">Welcome to {{ site_name }}!</h2>
    <p>Hi {{ user.first_name|default:user.username }},</p>
    <p>Thank you for joining {{ site_name }}. We're excited to help you plan your dream Kenyan adventure!</p>
    <p>With your new account, you can:</p>
    <ul>
        <li>Create custom safari itineraries</li>
        <li>Save your favorite destinations</li>
        <li>Get personalized recommendations</li>
    </ul>
    <p>
        <a href="{{ protocol }}://{{ domain }}{{ login_url }}" style="background-color: #198754; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login to your account</a>
    </p>
    <p>Best regards,<br>The {{ site_name }} Team</p>
</div>
                ''',
                'text_content': '''
Welcome to {{ site_name }}!

Hi {{ user.first_name|default:user.username }},

Thank you for joining {{ site_name }}. We're excited to help you plan your dream Kenyan adventure!

Login to your account: {{ protocol }}://{{ domain }}{{ login_url }}

Best regards,
The {{ site_name }} Team
                '''
            },
            {
                'name': 'Trip Created',
                'email_type': 'trip_created',
                'subject': 'Your Trip Itinerary: {{ itinerary.title }}',
                'html_content': '''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #198754;">Your Trip is Ready!</h2>
    <p>Hi {{ user.first_name|default:user.username }},</p>
    <p>Great news! Your itinerary <strong>{{ itinerary.title }}</strong> has been successfully created.</p>
    <p><strong>Trip Details:</strong></p>
    <ul>
        <li>Duration: {{ itinerary.duration_days }} days</li>
        <li>Destinations: {{ itinerary.destinations.count }}</li>
    </ul>
    <p>
        <a href="{{ protocol }}://{{ domain }}{{ trip_url }}" style="background-color: #198754; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Itinerary</a>
    </p>
    <p>Best regards,<br>The {{ site_name }} Team</p>
</div>
                ''',
                'text_content': '''
Your Trip is Ready!

Hi {{ user.first_name|default:user.username }},

Great news! Your itinerary {{ itinerary.title }} has been successfully created.

View Itinerary: {{ protocol }}://{{ domain }}{{ trip_url }}

Best regards,
The {{ site_name }} Team
                '''
            },
            {
                'name': 'Password Reset',
                'email_type': 'password_reset',
                'subject': 'Password Reset Request',
                'html_content': '''
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #198754;">Password Reset</h2>
    <p>Hi {{ user.first_name|default:user.username }},</p>
    <p>You requested a password reset for your {{ site_name }} account.</p>
    <p>Click the link below to reset your password:</p>
    <p>
        <a href="{{ protocol }}://{{ domain }}{{ reset_url }}" style="background-color: #198754; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
    </p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Best regards,<br>The {{ site_name }} Team</p>
</div>
                ''',
                'text_content': '''
Password Reset

Hi {{ user.first_name|default:user.username }},

You requested a password reset for your {{ site_name }} account.

Reset Password: {{ protocol }}://{{ domain }}{{ reset_url }}

If you didn't request this, please ignore this email.

Best regards,
The {{ site_name }} Team
                '''
            }
        ]

        for template_data in templates:
            template, created = EmailTemplate.objects.update_or_create(
                email_type=template_data['email_type'],
                defaults=template_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created template: {template.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated template: {template.name}'))
