"""
Template tags for static pages.
"""

from django import template
from core.models_pages import StaticPage, ContactInfo

register = template.Library()


@register.simple_tag
def get_footer_pages():
    """Get all published pages that should appear in footer."""
    return StaticPage.objects.filter(
        is_published=True,
        show_in_footer=True
    ).order_by('footer_order', 'title')


@register.simple_tag
def get_contact_info():
    """Get contact information for footer."""
    return ContactInfo.get_contact_info()
