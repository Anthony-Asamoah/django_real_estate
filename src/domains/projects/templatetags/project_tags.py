from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def format_price(price, currency):
    """{{ project.price|format_price:project.effective_currency }} → 'GH₵ 250,000'"""
    formatted = intcomma(price)
    if currency and currency.symbol:
        return f'{currency.symbol} {formatted}'
    return formatted
