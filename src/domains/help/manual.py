"""Loads the admin user manual from the markdown files in ./content."""
import re
from pathlib import Path

import markdown
import nh3

CONTENT_DIR = Path(__file__).parent / 'content'
_ATTRS = {'a': {'href', 'title'}, '*': {'id'}}


def _render(text):
    md = markdown.Markdown(extensions=['meta', 'toc', 'tables', 'fenced_code', 'sane_lists', 'attr_list'])
    html = md.convert(text)
    meta = {k: v[0] for k, v in md.Meta.items()}
    return nh3.clean(html, attributes=_ATTRS), meta


def get_sections(cms_url=''):
    """Section list ordered by the `order` front matter. Slug is the file name minus its numeric prefix."""
    sections = []
    for path in CONTENT_DIR.glob('*.md'):
        text = path.read_text(encoding='utf-8')
        # [[cms_url]] becomes a clickable full address, so the manual never hard-codes a domain.
        text = text.replace('[[cms_url]]', f'[{cms_url}]({cms_url})')
        html, meta = _render(text)
        sections.append({
            'slug': re.sub(r'^\d+-', '', path.stem),
            'title': meta.get('title', path.stem),
            'order': int(meta.get('order', 99)),
            'html': html,
        })
    return sorted(sections, key=lambda s: s['order'])
