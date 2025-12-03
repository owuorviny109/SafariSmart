"""
Module: core/models_pages.py
Purpose: Models for managing static pages (About, Privacy, Terms, etc.)

This module provides models for creating and managing static content pages
that can be edited from the Django admin panel.

Classes:
    StaticPage: Model for static content pages
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator


class ContactInfo(models.Model):
    """
    Singleton model for managing contact information and social links.
    
    Only one instance should exist. Editable from admin panel.
    
    Attributes:
        email (str): Contact email
        phone (str): Contact phone number
        location (str): Business location
        github_url (str): GitHub profile URL
        linkedin_url (str): LinkedIn profile URL
        twitter_url (str): Twitter profile URL
        portfolio_url (str): Portfolio website URL
        portfolio_text (str): Text for portfolio link
        about_text (str): Short about text for footer
    """
    
    # Contact Details
    email = models.EmailField(
        default="info@safarismart.co.ke",
        help_text="Contact email address"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number (e.g., +254 796 915 745)"
    )
    
    location = models.CharField(
        max_length=100,
        default="Nairobi, Kenya",
        help_text="Business location"
    )
    
    # Social Links
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter profile URL"
    )
    
    # Portfolio
    portfolio_url = models.URLField(
        blank=True,
        help_text="Portfolio website URL"
    )
    
    portfolio_text = models.CharField(
        max_length=50,
        default="Explore my work",
        help_text="Text for portfolio link"
    )
    
    # Footer Text
    about_text = models.TextField(
        default="Your intelligent trip planning platform for Kenya. Discover safaris, beaches, and unforgettable adventures.",
        help_text="Short description for footer"
    )
    
    creator_name = models.CharField(
        max_length=100,
        default="Vincent Owuor",
        help_text="Creator/developer name"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"
        
    def __str__(self) -> str:
        return "Contact Information"
        
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        """Prevent deletion of contact info."""
        pass
        
    @classmethod
    def get_contact_info(cls):
        """Get or create the singleton contact info instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class StaticPage(models.Model):
    """
    Model for managing static content pages.
    
    Allows admins to create and edit pages like About Us, Privacy Policy,
    Terms of Service, Contact, etc. from the admin panel.
    
    Attributes:
        title (str): Page title
        slug (str): URL-friendly identifier
        content (text): Page content (supports HTML)
        meta_description (str): SEO meta description
        is_published (bool): Whether page is visible
        show_in_footer (bool): Display link in footer
        footer_order (int): Order in footer menu
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        
    Example:
        >>> page = StaticPage.objects.create(
        ...     title="About Us",
        ...     content="<h1>About SafariSmart Kenya</h1><p>We are...</p>",
        ...     is_published=True
        ... )
    """
    
    # Page identification
    title = models.CharField(
        max_length=200,
        unique=True,
        help_text="Page title (e.g., 'About Us', 'Privacy Policy')"
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL slug (auto-generated from title)"
    )
    
    # Content
    content = models.TextField(
        validators=[MinLengthValidator(50)],
        help_text="Page content (HTML supported)"
    )
    
    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description (160 characters max)"
    )
    
    # Visibility
    is_published = models.BooleanField(
        default=True,
        help_text="Make page publicly visible"
    )
    
    # Footer menu
    show_in_footer = models.BooleanField(
        default=True,
        help_text="Show link in footer menu"
    )
    
    footer_order = models.IntegerField(
        default=0,
        help_text="Order in footer menu (lower numbers appear first)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Static Page"
        verbose_name_plural = "Static Pages"
        ordering = ['footer_order', 'title']
        
    def __str__(self) -> str:
        return self.title
        
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        """Get the URL for this page."""
        from django.urls import reverse
        return reverse('core:static_page', kwargs={'slug': self.slug})
