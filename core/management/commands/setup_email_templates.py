"""
Management command to create default email templates.

Usage: python manage.py setup_email_templates
"""

from django.core.management.base import BaseCommand
from core.models_email import EmailTemplate


class Command(BaseCommand):
    help = 'Create default email templates'
    
    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Welcome Email',
                'email_type': 'welcome',
                'subject': 'Welcome to SafariSmart Kenya, {{ user.first_name|default:user.username }}!',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to SafariSmart Kenya</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #198754; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f8f9fa; padding: 30px; }
        .footer { background: #e9ecef; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #198754; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }
        .highlight { background: #fff3cd; padding: 15px; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦁 Welcome to SafariSmart Kenya!</h1>
            <p>Your Gateway to Amazing Adventures</p>
        </div>
        
        <div class="content">
            <h2>Hello {{ user.first_name|default:user.username }}!</h2>
            
            <p>Welcome to SafariSmart Kenya! We're thrilled to have you join our community of adventure seekers.</p>
            
            <div class="highlight">
                <h3>🎯 What You Can Do Now:</h3>
                <ul>
                    <li><strong>Plan Your Trip:</strong> Use our AI-powered trip planner</li>
                    <li><strong>Explore Destinations:</strong> Discover Kenya's amazing locations</li>
                    <li><strong>Save Itineraries:</strong> Keep your favorite trips for later</li>
                    <li><strong>Get Recommendations:</strong> Personalized suggestions just for you</li>
                </ul>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ login_url }}" class="button">Start Planning Your Adventure</a>
            </p>
            
            <p>If you have any questions, our team is here to help. Just reply to this email!</p>
            
            <p>Happy travels!<br>
            The SafariSmart Kenya Team</p>
        </div>
        
        <div class="footer">
            <p>SafariSmart Kenya - Discover. Plan. Adventure.</p>
            <p><small>This email was sent because you created an account with us.</small></p>
        </div>
    </div>
</body>
</html>
                ''',
                'text_content': '''
Welcome to SafariSmart Kenya, {{ user.first_name|default:user.username }}!

We're thrilled to have you join our community of adventure seekers.

What You Can Do Now:
- Plan Your Trip: Use our AI-powered trip planner
- Explore Destinations: Discover Kenya's amazing locations  
- Save Itineraries: Keep your favorite trips for later
- Get Recommendations: Personalized suggestions just for you

Start planning your adventure: {{ login_url }}

If you have any questions, our team is here to help. Just reply to this email!

Happy travels!
The SafariSmart Kenya Team

SafariSmart Kenya - Discover. Plan. Adventure.
                ''',
                'available_variables': '{{ user.first_name }}, {{ user.username }}, {{ user.email }}, {{ login_url }}, {{ site_name }}'
            },
            
            {
                'name': 'Trip Created Notification',
                'email_type': 'trip_created',
                'subject': 'Your {{ itinerary.title }} trip is ready! 🎉',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Your Trip is Ready!</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #198754; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f8f9fa; padding: 30px; }
        .footer { background: #e9ecef; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; }
        .button { display: inline-block; background: #198754; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; }
        .trip-details { background: white; padding: 20px; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Your Trip is Ready!</h1>
            <p>{{ itinerary.title }}</p>
        </div>
        
        <div class="content">
            <h2>Hello {{ user.first_name|default:user.username }}!</h2>
            
            <p>Great news! Your personalized Kenya adventure is ready for you.</p>
            
            <div class="trip-details">
                <h3>📋 Trip Summary:</h3>
                <ul>
                    <li><strong>Duration:</strong> {{ itinerary.duration_days }} days</li>
                    <li><strong>Budget:</strong> KSh {{ itinerary.total_budget }}</li>
                    <li><strong>Travel Type:</strong> {{ itinerary.travel_type }}</li>
                    <li><strong>Group Size:</strong> {{ itinerary.adults_count }} adults{% if itinerary.children_count %}, {{ itinerary.children_count }} children{% endif %}</li>
                </ul>
            </div>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ trip_url }}" class="button">View Your Complete Itinerary</a>
            </p>
            
            <p><strong>What's Next?</strong></p>
            <ul>
                <li>Review your detailed day-by-day itinerary</li>
                <li>Share it with your travel companions</li>
                <li>Save it to your dashboard for easy access</li>
                <li>Contact local tour operators for bookings</li>
            </ul>
            
            <p>Have questions or want to modify your trip? Just reply to this email!</p>
            
            <p>Safe travels!<br>
            The SafariSmart Kenya Team</p>
        </div>
        
        <div class="footer">
            <p>SafariSmart Kenya - Your AI Travel Companion</p>
        </div>
    </div>
</body>
</html>
                ''',
                'available_variables': '{{ user.first_name }}, {{ user.username }}, {{ itinerary.title }}, {{ itinerary.duration_days }}, {{ itinerary.total_budget }}, {{ trip_url }}'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = EmailTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                # Update existing template
                for key, value in template_data.items():
                    if key != 'name':
                        setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated template: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nEmail templates setup complete!\n'
                f'Created: {created_count}\n'
                f'Updated: {updated_count}'
            )
        )