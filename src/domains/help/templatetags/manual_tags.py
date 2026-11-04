from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def manual_url(section, anchor=''):
    """URL of a manual section, optionally to a heading id. Use with target="_blank" rel="noopener"."""
    url = reverse('manual_section', kwargs={'slug': section})
    return f'{url}#{anchor}' if anchor else url
