from django.contrib.auth.models import User

# Reset password for the superuser
username = 'owuorvincent069@gmail.com'
new_password = 'admin123'  # Simple password for local development

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    print(f"✓ Password successfully reset for user: {username}")
    print(f"✓ New password: {new_password}")
    print(f"\nYou can now login at http://127.0.0.1:8000/admin/")
    print(f"Username: {username}")
    print(f"Password: {new_password}")
except User.DoesNotExist:
    print(f"✗ User {username} not found")
