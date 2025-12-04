import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safarismart.settings')
django.setup()

from core.models_email import EmailLog, EmailTemplate, EmailSettings

print('=== EMAIL SYSTEM TEST REPORT ===\n')

print('Email Templates:')
for t in EmailTemplate.objects.all():
    print(f'  - {t.get_email_type_display()}: {t.name} (Active: {t.is_active})')

print('\nEmail Settings:')
s = EmailSettings.get_settings()
print(f'  - Notifications Enabled: {s.enable_email_notifications}')
print(f'  - Welcome Emails: {s.enable_welcome_emails}')
print(f'  - Trip Notifications: {s.enable_trip_notifications}')
print(f'  - Company: {s.company_name}')

print('\nRecent Email Logs (Last 10):')
for i, log in enumerate(EmailLog.objects.order_by('-created_at')[:10]):
    print(f'  {i+1}. [{log.status.upper()}] {log.subject}')
    print(f'      To: {log.recipient_email}')
    print(f'      Template: {log.template.name}')
    print(f'      Created: {log.created_at}')
    if log.error_message:
        print(f'      Error: {log.error_message}')
    print()

print(f'Total Emails Sent: {EmailLog.objects.filter(status="sent").count()}')
print(f'Total Emails Failed: {EmailLog.objects.filter(status="failed").count()}')
