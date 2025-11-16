"""
Custom template filters for dictionary operations.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    
    Usage in template:
        {{ my_dict|get_item:"key_name" }}
    """
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
