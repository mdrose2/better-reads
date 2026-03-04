from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def safe_message(message):
    """Mark message as safe HTML to allow links in messages."""
    return mark_safe(message)