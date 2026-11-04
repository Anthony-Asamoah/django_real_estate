from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render

from .manual import get_sections


def manual(request, slug=None):
    sections = get_sections(cms_url=f'{settings.WAGTAILADMIN_BASE_URL.rstrip("/")}/cms')
    if slug is None:
        return redirect('manual_section', slug=sections[0]['slug'])
    i = next((n for n, s in enumerate(sections) if s['slug'] == slug), None)
    if i is None:
        raise Http404
    return render(request, 'help/manual.html', {
        'sections': sections,
        'current': sections[i],
        'prev': sections[i - 1] if i > 0 else None,
        'next': sections[i + 1] if i + 1 < len(sections) else None,
    })
