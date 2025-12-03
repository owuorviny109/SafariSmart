from django.template import Template, Context
from django.utils import timezone
from django.db import models
import logging

logger = logging.getLogger(__name__)


class EmailTemplate(models.Model):
    """
    Email template model for managing different types of emails.
    
    Allows admins to edit email content through Django admin.
    """
    
    EMAIL_TYPES = [
        ('welcome', 'Welcome Email'),
        ('trip_created', 'Trip Created'),
        ('trip_shared', 'Trip Shared'),
        ('password_reset', 'Password Reset'),
        ('account_verification', 'Account Verification'),
        ('newsletter', 'Newsletter'),
        ('booking_confirmation', 'Booking Confirmation'),
        ('custom', 'Custom Email'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES)
    subject = models.CharField(max_length=200)
    html_content = models.TextField(help_text="HTML email content with template variables")
    text_content = models.TextField(help_text="Plain text email content", blank=True)
    
    # Template variables help
    available_variables = models.TextField(
        help_text="Available template variables (for reference)",
        blank=True,
        default="Common variables: {{ user.first_name }}, {{ user.username }}, {{ user.email }}"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['email_type', 'name']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    def __str__(self):
        return f"{self.get_email_type_display()} - {self.name}"
    
    def render_subject(self, context_data):
        """Render subject with context data"""
        template = Template(self.subject)
        context = Context(context_data)
        return template.render(context)
    
    def render_html_content(self, context_data):
        """Render HTML content with context data"""
        template = Template(self.html_content)
        context = Context(context_data)
        return template.render(context)
    
    def render_text_content(self, context_data):
        """Render text content with context data"""
        if self.text_content:
            template = Template(self.text_content)
            context = Context(context_data)
            return template.render(context)
        return None
    
    def send_email(self, recipient_email, context_data, from_email=None):
        """
        Send email using this template
        
        Args:
            recipient_email (str): Recipient email address
            context_data (dict): Template context variables
            from_email (str): From email address (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            subject = self.render_subject(context_data)
            html_content = self.render_html_content(context_data)
            text_content = self.render_text_content(context_data)
            
            # Create email log
            email_log = EmailLog.objects.create(
                template=self,
                recipient_email=recipient_email,
                subject=subject,
                status='sending'
            )
            
            # Send email
            send_mail(
                subject=subject,
                message=text_content or '',
                from_email=from_email,
                recipient_list=[recipient_email],
                html_message=html_content,
                fail_silently=False
            )
            
            # Update log
            email_log.status = 'sent'
            email_log.sent_at = timezone.now()
            email_log.save()
            
            logger.info(f"Email sent successfully: {subject} to {recipient_email}")
            return True
            
        except Exception as e:
            # Update log with error
            if 'email_log' in locals():
                email_log.status = 'failed'
                email_log.error_message = str(e)
                email_log.save()
            
            logger.error(f"Failed to send email: {str(e)}")
            return False


class EmailLog(models.Model):
    """
    Log of all emails sent through the system.
    
    Tracks email delivery status and provides audit trail.
    """
    
    STATUS_CHOICES = [
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='logs')
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sending')
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
    
    def __str__(self):
        return f"{self.subject} to {self.recipient_email} - {self.status}"


class EmailSettings(models.Model):
    """
    Email configuration settings manageable through Django admin.
    
    Allows business to control email addresses, SMTP settings, and branding.
    """
    
    # Singleton pattern - only one instance allowed
    class Meta:
        verbose_name = 'Email Settings'
        verbose_name_plural = 'Email Settings'
    
    # From Email Addresses
    default_from_email = models.EmailField(
        default='SafariSmart Kenya <noreply@safarismart.co.ke>',
        help_text='Default email address for outgoing emails'
    )
    
    support_email = models.EmailField(
        default='support@safarismart.co.ke',
        help_text='Support email address for customer inquiries'
    )
    
    booking_email = models.EmailField(
        default='bookings@safarismart.co.ke',
        help_text='Email address for booking confirmations'
    )
    
    marketing_email = models.EmailField(
        default='hello@safarismart.co.ke',
        help_text='Email address for marketing emails'
    )
    
    # Email Branding
    company_name = models.CharField(
        max_length=100,
        default='SafariSmart Kenya',
        help_text='Company name to display in emails'
    )
    
    company_tagline = models.CharField(
        max_length=200,
        default='Your Gateway to Amazing Adventures',
        help_text='Company tagline for email footers'
    )
    
    # SMTP Settings (optional - can override .env)
    smtp_host = models.CharField(
        max_length=100,
        blank=True,
        help_text='SMTP server host (leave blank to use .env settings)'
    )
    
    smtp_port = models.IntegerField(
        null=True,
        blank=True,
        help_text='SMTP server port (leave blank to use .env settings)'
    )
    
    smtp_username = models.CharField(
        max_length=100,
        blank=True,
        help_text='SMTP username (leave blank to use .env settings)'
    )
    
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text='Use TLS for SMTP connection'
    )
    
    # Email Features
    enable_email_notifications = models.BooleanField(
        default=True,
        help_text='Enable/disable all email notifications'
    )
    
    enable_welcome_emails = models.BooleanField(
        default=True,
        help_text='Send welcome emails to new users'
    )
    
    enable_trip_notifications = models.BooleanField(
        default=True,
        help_text='Send notifications when users create trips'
    )
    
    enable_marketing_emails = models.BooleanField(
        default=False,
        help_text='Enable marketing/newsletter emails'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        if not self.pk and EmailSettings.objects.exists():
            # If trying to create a new instance when one already exists
            raise ValueError('Only one EmailSettings instance is allowed')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the email settings instance (create if doesn't exist)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def __str__(self):
        return f"Email Settings - {self.company_name}"


class EmailService:
    """
    Service class for sending emails using templates.
    
    Provides a clean interface for sending different types of emails.
    """
    
    @staticmethod
    def get_from_email(email_type='default'):
        """Get appropriate from email based on type"""
        settings = EmailSettings.get_settings()
        
        email_map = {
            'support': settings.support_email,
            'booking': settings.booking_email,
            'marketing': settings.marketing_email,
            'default': settings.default_from_email,
        }
        
        return email_map.get(email_type, settings.default_from_email)
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new user"""
        settings = EmailSettings.get_settings()
        
        if not settings.enable_email_notifications or not settings.enable_welcome_emails:
            logger.info("Welcome emails are disabled")
            return False
            
        try:
            template = EmailTemplate.objects.get(email_type='welcome', is_active=True)
            context = {
                'user': user,
                'site_name': settings.company_name,
                'company_tagline': settings.company_tagline,
                'login_url': '/accounts/login/',
                'support_email': settings.support_email,
            }
            from_email = EmailService.get_from_email('default')
            return template.send_email(user.email, context, from_email)
        except EmailTemplate.DoesNotExist:
            logger.warning("Welcome email template not found")
            return False
    
    @staticmethod
    def send_trip_created_email(user, itinerary):
        """Send email when user creates a trip"""
        settings = EmailSettings.get_settings()
        
        if not settings.enable_email_notifications or not settings.enable_trip_notifications:
            logger.info("Trip notification emails are disabled")
            return False
            
        try:
            template = EmailTemplate.objects.get(email_type='trip_created', is_active=True)
            context = {
                'user': user,
                'itinerary': itinerary,
                'trip_url': f'/itinerary/{itinerary.share_code}/',
                'site_name': settings.company_name,
                'company_tagline': settings.company_tagline,
                'support_email': settings.support_email,
            }
            from_email = EmailService.get_from_email('default')
            return template.send_email(user.email, context, from_email)
        except EmailTemplate.DoesNotExist:
            logger.warning("Trip created email template not found")
            return False
    
    @staticmethod
    def send_custom_email(template_name, recipient_email, context_data, email_type='default'):
        """Send custom email using template name"""
        settings = EmailSettings.get_settings()
        
        if not settings.enable_email_notifications:
            logger.info("Email notifications are disabled")
            return False
            
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)
            # Add company info to context
            context_data.update({
                'site_name': settings.company_name,
                'company_tagline': settings.company_tagline,
                'support_email': settings.support_email,
            })
            from_email = EmailService.get_from_email(email_type)
            return template.send_email(recipient_email, context_data, from_email)
        except EmailTemplate.DoesNotExist:
            logger.warning(f"Email template '{template_name}' not found")
            return False