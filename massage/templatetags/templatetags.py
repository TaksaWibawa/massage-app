from datetime import timedelta
from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def add_days(value, days):
    return value + timedelta(days=int(days))

@register.filter
def sum_list(value, arg):
    return sum(getattr(item, arg) for item in value)

@register.filter
def currency(value):
    return f'{round(value/1000)}k' if value >= 1000 else value

@register.filter
def currency_format_dot(value):
    if isinstance(value, (int, float, Decimal)):
        value = int(value)
        return '{:,}'.format(value).replace(',', '.')
    else:
        return value

@register.filter
def percentage(value):
    if isinstance(value, (int, float, Decimal)):
        value = round(value)
        return f'{value}%' if value >= 0 else f'({abs(value)}%)'
    else:
        return value

@register.filter
def apply_fee(price, fee_percentage):
    return price * (fee_percentage / 100)