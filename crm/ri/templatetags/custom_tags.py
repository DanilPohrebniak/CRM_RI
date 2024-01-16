from django import template

register = template.Library()

@register.filter
def get_field_value(item, field_name):
    return getattr(item, field_name, '')