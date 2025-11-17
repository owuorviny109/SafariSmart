"""
Module: accounts/views.py
Purpose: View layer for user authentication and account management

This module contains view classes for user authentication using Django's
built-in authentication system. All views follow OOP principles and use
Class-Based Views (CBV).

Classes:
    LoginView: Handles user login
    RegisterView: Handles user registration
    LogoutView: Handles user logout
    
Author: SafariSmart Kenya Team
Date: 2025-11-16
"""

from typing import Dict, Any
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import StyledAuthenticationForm, StyledUserCreationForm
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class UserLoginView(DjangoLoginView):
    """
    Handle user login using Django's built-in authentication.
    
    This view extends Django's LoginView to provide custom template
    and redirect behavior while maintaining all built-in security features.
    
    Attributes:
        template_name (str): Path to login template
        form_class: Custom styled authentication form
        redirect_authenticated_user (bool): Redirect if already logged in
        
    Example:
        URL: /accounts/login/
        GET: Display login form
        POST: Authenticate and redirect to dashboard
    """
    
    template_name = 'accounts/login.html'
    form_class = StyledAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self) -> str:
        """
        Get URL to redirect to after successful login.
        
        Returns:
            str: URL path for redirect
        """
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('core:dashboard')
    
    def form_valid(self, form: AuthenticationForm) -> Any:
        """
        Handle valid login form submission.
        
        Args:
            form (AuthenticationForm): Validated login form
            
        Returns:
            HttpResponse: Redirect response
        """
        logger.info(f"User {form.get_user().username} logged in successfully")
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)
    
    def form_invalid(self, form: AuthenticationForm) -> Any:
        """
        Handle invalid login form submission.
        
        Args:
            form (AuthenticationForm): Invalid login form
            
        Returns:
            HttpResponse: Rendered template with errors
        """
        logger.warning(f"Failed login attempt for username: {form.data.get('username')}")
        messages.error(self.request, "Invalid email or password. Please try again.")
        return super().form_invalid(form)


class UserRegisterView(CreateView):
    """
    Handle user registration.
    
    This view creates new user accounts using custom styled
    UserCreationForm with email field and Bootstrap styling.
    
    Attributes:
        model: User model
        form_class: Custom styled registration form
        template_name (str): Path to registration template
        success_url: URL to redirect after successful registration
        
    Example:
        URL: /accounts/register/
        GET: Display registration form
        POST: Create user and redirect to login
    """
    
    model = User
    form_class = StyledUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Redirect authenticated users away from registration.
        
        Args:
            request: HTTP request object
            
        Returns:
            HttpResponse: Redirect or normal response
        """
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form: UserCreationForm) -> Any:
        """
        Handle valid registration form submission.
        
        Creates user account and logs them in automatically.
        
        Args:
            form (UserCreationForm): Validated registration form
            
        Returns:
            HttpResponse: Redirect response
        """
        # Save the user
        response = super().form_valid(form)
        
        # Log the user in automatically
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            logger.info(f"New user registered and logged in: {username}")
            messages.success(
                self.request,
                f"Welcome to SafariSmart Kenya, {username}! Your account has been created."
            )
            return redirect('core:dashboard')
        
        logger.info(f"New user registered: {username}")
        messages.success(
            self.request,
            "Account created successfully! Please log in."
        )
        return response
    
    def form_invalid(self, form: UserCreationForm) -> Any:
        """
        Handle invalid registration form submission.
        
        Args:
            form (UserCreationForm): Invalid registration form
            
        Returns:
            HttpResponse: Rendered template with errors
        """
        logger.warning(f"Failed registration attempt: {form.errors}")
        messages.error(
            self.request,
            "Registration failed. Please correct the errors below."
        )
        return super().form_invalid(form)


class UserLogoutView(View):
    """
    Handle user logout.
    
    This view logs out the current user and redirects to landing page.
    
    Example:
        URL: /accounts/logout/
        GET: Logout user and redirect
    """
    
    def get(self, request) -> Any:
        """
        Handle logout request.
        
        Args:
            request: HTTP request object
            
        Returns:
            HttpResponse: Redirect to landing page
        """
        username = request.user.username if request.user.is_authenticated else 'Unknown'
        logout(request)
        logger.info(f"User {username} logged out")
        messages.success(request, "You have been logged out successfully.")
        return redirect('core:landing')
    
    def post(self, request) -> Any:
        """
        Handle logout POST request (for CSRF protection).
        
        Args:
            request: HTTP request object
            
        Returns:
            HttpResponse: Redirect to landing page
        """
        return self.get(request)
