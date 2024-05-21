from django import template

register = template.Library()

@register.filter
def currency(value):
    return f'{round(value/1000)}k' if value >= 1000 else value