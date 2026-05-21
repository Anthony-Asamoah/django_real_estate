from django.utils.html import format_html, format_html_join
from django.utils.timesince import timesince
from wagtail.admin.panels import Panel

_CIRCLE = (
    'display:flex;width:38px;height:38px;border-radius:50%;'
    'overflow:hidden;flex-shrink:0;box-shadow:0 1px 4px rgba(0,0,0,.35)'
)
_HALF = 'display:block;width:50%;height:100%'
_MINI = (
    'display:inline-block;width:18px;height:18px;border-radius:4px;'
    'box-shadow:0 1px 2px rgba(0,0,0,.25)'
)


class ColorPresetsPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        def render_html(self, parent_context=None):
            from .models import ColorPreset
            presets = list(ColorPreset.objects.all())
            if not presets:
                return format_html(
                    '<div class="color-presets-panel">'
                    '<p class="presets-heading">Presets</p>'
                    '<p style="color:#888;font-size:.83rem;font-style:italic;margin:0">'
                    'No presets yet — save one below.</p>'
                    '</div>'
                )
            buttons = format_html_join(
                '\n',
                '<button type="button" class="color-swatch-btn"'
                ' data-primary="{}" data-secondary="{}" title="{}">'
                '<span style="' + _CIRCLE + '">'
                '<span style="' + _HALF + ';background:{}"></span>'
                '<span style="' + _HALF + ';background:{}"></span>'
                '</span>'
                '<span class="swatch-label">{}</span>'
                '</button>',
                [
                    (p.primary_color, p.secondary_color, p.name,
                     p.primary_color, p.secondary_color, p.name)
                    for p in presets
                ],
            )
            return format_html(
                '<div class="color-presets-panel">'
                '<p class="presets-heading">Presets</p>'
                '<div class="presets-row">{}</div>'
                '</div>',
                buttons,
            )


class ColorSavePanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        def render_html(self, parent_context=None):
            return format_html(
                '<div class="save-preset-row">'
                '<div class="save-preset-form">'
                '<input type="text" class="preset-name-input"'
                ' placeholder="Name this palette…" maxlength="60" />'
                '<button type="button" class="button button-small save-preset-btn">Save as Preset</button>'
                '<span class="save-preset-feedback"></span>'
                '</div>'
                '</div>'
            )


class ColorHistoryPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        def render_html(self, parent_context=None):
            if not self.instance or not self.instance.pk:
                return format_html('')
            history = list(self.instance.color_history.all()[:10])
            if not history:
                return format_html(
                    '<div class="color-history-panel">'
                    '<details><summary>Color History</summary>'
                    '<p style="color:#888;font-size:.83rem;padding:.5rem 0;margin:0">'
                    'No history yet — it appears after the first color change.</p>'
                    '</details></div>'
                )
            rows = format_html_join(
                '\n',
                '<div class="history-row">'
                '<span style="display:inline-flex;gap:4px;align-items:center;flex-shrink:0">'
                '<span style="' + _MINI + ';background:{}" title="Primary {}"></span>'
                '<span style="' + _MINI + ';background:{}" title="Secondary {}"></span>'
                '</span>'
                '<span class="history-time">{} ago</span>'
                '<button type="button"'
                ' class="history-restore button button-small button-secondary"'
                ' data-primary="{}" data-secondary="{}">Restore</button>'
                '</div>',
                [
                    (
                        h.primary_color, h.primary_color,
                        h.secondary_color, h.secondary_color,
                        timesince(h.changed_at),
                        h.primary_color, h.secondary_color,
                    )
                    for h in history
                ],
            )
            return format_html(
                '<div class="color-history-panel">'
                '<details><summary>Color History ({} saved)</summary>'
                '<div class="history-list">{}</div>'
                '</details></div>',
                len(history),
                rows,
            )
