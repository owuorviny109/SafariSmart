"""
Module: accounts/forms_custom.py
Purpose: Custom authentication forms extending Django defaults
"""

from django.contrib.auth.forms import PasswordResetForm
from core.models_email import EmailService
import logging

logger = logging.getLogger(__name__)

class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form that uses EmailService.
    
    Overrides the save method to use our centralized EmailService
    instead of Django's default send_mail, ensuring:
    1. Emails are logged in EmailLog
    2. Global email settings (enable/disable) are respected
    3. Custom templates are used
    """
    
    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        email = self.cleaned_data["email"]
        
        # We iterate over all users with this email to handle multiple users with same email
        # (though typically email should be unique)
        for user in self.get_users(email):
            if not domain_override:
                current_site = self.get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
                
            context = {
                'email': email,
                'domain': domain,
                'site_name': site_name,
                'uid': self.get_user_id(user),
                'user': user,
                'token': self.get_token(user, token_generator),
                'protocol': 'https' if use_https else 'http',
                **(extra_email_context or {}),
            }
            
            # Use our custom EmailService
            # We construct the reset URL part manually or let the template handle it
            # The standard Django template expects 'uid' and 'token'
            # Our EmailService.send_password_reset_email expects 'user' and 'context'
            
            # Add reset_url for our custom template
            context['reset_url'] = f"/accounts/password-reset-confirm/{context['uid']}/{context['token']}/"
            
            success = EmailService.send_password_reset_email(user, context)
            
            if success:
                logger.info(f"Password reset email sent to {email}")
            else:
                logger.error(f"Failed to send password reset email to {email}")
                
        return email
    
    def get_current_site(self, request):
        from django.contrib.sites.shortcuts import get_current_site
        return get_current_site(request)
        
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                '%s__iexact' % email_field_name: email,
                'is_active': True,
            }
        )
        return (
            u for u in active_users
            if u.has_usable_password() and
            self.get_user_id(u) is not None
        )

    def get_user_id(self, user):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        return urlsafe_base64_encode(force_bytes(user.pk))

    def get_token(self, user, token_generator=None):
        from django.contrib.auth.tokens import default_token_generator
        if token_generator is None:
            token_generator = default_token_generator
        return token_generator.make_token(user)
