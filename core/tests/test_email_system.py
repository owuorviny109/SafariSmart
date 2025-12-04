from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core import mail
from core.models_email import EmailService, EmailTemplate, EmailLog, EmailSettings
from accounts.forms_custom import CustomPasswordResetForm
from core.models import Itinerary
import json

class EmailSystemTest(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test'
        )
        
        # Create settings
        self.settings = EmailSettings.get_settings()
        self.settings.enable_email_notifications = True
        self.settings.save()
        
        # Create templates
        EmailTemplate.objects.create(
            name='Welcome Email',
            email_type='welcome',
            subject='Welcome {{ user.first_name }}',
            html_content='<p>Welcome {{ user.username }}</p>',
            text_content='Welcome {{ user.username }}'
        )
        
        EmailTemplate.objects.create(
            name='Password Reset',
            email_type='password_reset',
            subject='Reset Password',
            html_content='<p>Link: {{ reset_url }}</p>',
            text_content='Link: {{ reset_url }}'
        )
        
        EmailTemplate.objects.create(
            name='Trip Created',
            email_type='trip_created',
            subject='Trip: {{ itinerary.title }}',
            html_content='<p>Trip URL: {{ trip_url }}</p>',
            text_content='Trip URL: {{ trip_url }}'
        )

    def test_welcome_email(self):
        """Test welcome email sending"""
        success = EmailService.send_welcome_email(self.user)
        self.assertTrue(success)
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome Test')
        self.assertIn('Welcome testuser', mail.outbox[0].body)
        
        # Check log
        log = EmailLog.objects.first()
        self.assertEqual(log.recipient_email, 'test@example.com')
        self.assertEqual(log.status, 'sent')

    def test_password_reset_form(self):
        """Test custom password reset form"""
        form = CustomPasswordResetForm(data={'email': 'test@example.com'})
        self.assertTrue(form.is_valid())
        
        # Mock request
        factory = RequestFactory()
        request = factory.get('/accounts/password-reset/')
        
        # Save form (sends email)
        form.save(request=request)
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Reset Password')
        
        # Check log
        log = EmailLog.objects.filter(subject='Reset Password').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.recipient_email, 'test@example.com')

    def test_trip_created_email(self):
        """Test trip created email"""
        itinerary = Itinerary.objects.create(
            user=self.user,
            title='My Safari',
            duration_days=5,
            adults_count=2,
            children_count=0,
            travel_type='couple',
            total_budget=100000,
            budget_category='mid-range',
            itinerary_data={'content': 'test'},
            cost_breakdown={}
        )
        
        success = EmailService.send_trip_created_email(self.user, itinerary)
        self.assertTrue(success)
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Trip: My Safari')
