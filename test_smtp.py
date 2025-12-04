import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

print('=== CURRENT EMAIL CONFIGURATION ===\n')
print(f'Backend: {config("EMAIL_BACKEND", default="console")}')
print(f'Host: {config("EMAIL_HOST", default="NOT SET")}')
print(f'Port: {config("EMAIL_PORT", default="NOT SET")}')
print(f'Use TLS: {config("EMAIL_USE_TLS", default="NOT SET")}')
print(f'Username: {config("EMAIL_HOST_USER", default="NOT SET")}')
print(f'Password: {"***SET***" if config("EMAIL_HOST_PASSWORD", default="") else "NOT SET"}')
print(f'From Email: {config("DEFAULT_FROM_EMAIL", default="NOT SET")}')

print('\n=== TESTING EMAIL SENDING ===\n')

# Test if we can send an email
from django.core.mail import send_mail
from core.models_email import EmailLog

try:
    # Try sending a test email
    result = send_mail(
        subject='Test Email - SMTP Configuration Check',
        message='This is a test email to verify SMTP is working.',
        from_email=config('DEFAULT_FROM_EMAIL'),
        recipient_list=[config('EMAIL_HOST_USER')],  # Send to yourself
        fail_silently=False,
    )
    print(f'✅ Email sent successfully! Result: {result}')
    print(f'Check your inbox at: {config("EMAIL_HOST_USER")}')
except Exception as e:
    print(f'❌ Email sending failed: {e}')

print(f'\nTotal emails in log: {EmailLog.objects.count()}')
print(f'Recent email status: {EmailLog.objects.order_by("-created_at").first().status if EmailLog.objects.exists() else "No emails"}')
