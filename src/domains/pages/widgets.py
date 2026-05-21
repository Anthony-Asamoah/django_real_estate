from django.forms.widgets import Input, TextInput
from django.utils.html import mark_safe


class ColorInput(Input):
    input_type = 'color'


_FA_ICONS = [
    'fa-home', 'fa-building', 'fa-hard-hat', 'fa-hammer', 'fa-wrench', 'fa-tools',
    'fa-paint-brush', 'fa-paint-roller', 'fa-ruler', 'fa-ruler-combined',
    'fa-drafting-compass', 'fa-pencil-ruler', 'fa-draw-polygon',
    'fa-fire', 'fa-bolt', 'fa-plug', 'fa-snowflake', 'fa-fan',
    'fa-leaf', 'fa-tree', 'fa-water', 'fa-faucet',
    'fa-door-open', 'fa-window-maximize', 'fa-warehouse',
    'fa-truck', 'fa-truck-loading', 'fa-dolly',
    'fa-clipboard-list', 'fa-clipboard-check', 'fa-tasks',
    'fa-star', 'fa-check-circle', 'fa-award', 'fa-medal', 'fa-trophy',
    'fa-users', 'fa-user-tie', 'fa-user-hard-hat', 'fa-handshake', 'fa-hands-helping',
    'fa-phone', 'fa-envelope', 'fa-map-marker-alt', 'fa-map-marker',
    'fa-calendar-check', 'fa-clock', 'fa-history',
    'fa-chart-bar', 'fa-chart-line', 'fa-cog', 'fa-sliders-h',
    'fa-search', 'fa-arrow-right', 'fa-angle-right', 'fa-shield-alt',
    'fa-lightbulb', 'fa-key', 'fa-lock', 'fa-lock-open',
    'fa-couch', 'fa-bath', 'fa-bed', 'fa-utensils',
    'fa-solar-panel', 'fa-recycle', 'fa-seedling',
    'fa-wifi', 'fa-camera', 'fa-video', 'fa-mobile-alt',
]


class IconInput(TextInput):
    """Text input with a live Font Awesome icon preview and autocomplete suggestions."""

    def render(self, name, value, attrs=None, renderer=None):
        attrs = self.build_attrs(self.attrs, attrs)
        input_id = attrs.get('id', name)
        list_id = input_id + '_iconlist'
        preview_id = input_id + '_preview'
        attrs['list'] = list_id
        attrs['autocomplete'] = 'off'
        attrs['placeholder'] = 'e.g. fa-home'

        html = super().render(name, value, attrs, renderer)

        options = ''.join(f'<option value="{icon}">' for icon in _FA_ICONS)
        current_icon = value or 'fa-question'
        html += (
            f'<datalist id="{list_id}">{options}</datalist>'
            f'<div style="margin-top:8px;display:flex;align-items:center;gap:12px;">'
            f'  <span id="{preview_id}" style="font-size:2rem;width:44px;text-align:center;'
            f'        line-height:1;color:#10284e;">'
            f'    <i class="fas {current_icon}"></i>'
            f'  </span>'
            f'  <span style="color:#888;font-size:.8rem;">Icon preview — start typing or pick from the list</span>'
            f'</div>'
            f'<script>'
            f'(function(){{'
            f'  var inp = document.getElementById("{input_id}");'
            f'  var prev = document.getElementById("{preview_id}");'
            f'  if (inp && prev) {{'
            f'    inp.addEventListener("input", function(){{'
            f'      prev.innerHTML = \'<i class="fas \' + this.value + \'"></i>\';'
            f'    }});'
            f'  }}'
            f'}})();'
            f'</script>'
        )
        return mark_safe(html)
