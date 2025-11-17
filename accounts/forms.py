"""
Module: accounts/forms.py
Purpose: Custom forms for user authentication

This module contains custom form classes that extend Django's built-in
authentication forms with Bootstrap styling.

Classes:
    StyledAuthenticationForm: Login form with Bootstrap classes
    StyledUserCreationForm: Registration form with Bootstrap classes
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class StyledAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with Bootstrap styling.
    
    Extends Django's AuthenticationForm to add Bootstrap CSS classes
    to form fields for consistent styling.
    
    Example:
        >>> form = StyledAuthenticationForm()
        >>> form.fields['username'].widget.attrs['class']
        'form-control'
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Bootstrap classes."""
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class StyledUserCreationForm(UserCreationForm):
    """
    Custom user creation form with Bootstrap styling.
    
    Extends Django's UserCreationForm to add Bootstrap CSS classes
    and additional fields like email.
    
    Attributes:
        email: Email field (required)
        
    Example:
        >>> form = StyledUserCreationForm()
        >>> 'email' in form.fields
        True
    """
    
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    
    class Meta:
        """Form metadata."""
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with Bootstrap classes."""
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name != 'email':  # Email already has placeholder
                field.widget.attrs['placeholder'] = field.label
    
    def save(self, commit=True):
        """
        Save user with email.
        
        Args:
            commit (bool): Whether to save to database
            
        Returns:
            User: Created user instance
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
