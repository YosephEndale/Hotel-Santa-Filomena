from django import template

register = template.Library()

@register.filter
def fmt_time(value):
    """Format a time field as HH:MM."""
    if not value:
        return ''
    return value.strftime('%H:%M')