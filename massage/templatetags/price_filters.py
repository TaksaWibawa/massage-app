from django import template

register = template.Library()

@register.filter
def currency(value):
    return f'{round(value/1000)}k' if value >= 1000 else value

@register.filter
def currency_format_dot(value):
    return '{:,}'.format(value).replace(',', '.')

@register.filter
def percentage(value):
    return f'{value}%' if value >= 0 else f'({abs(value)}%)'