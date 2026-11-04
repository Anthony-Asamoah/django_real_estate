import json

from django import forms
from django.utils.html import format_html


class LandPlanWidget(forms.HiddenInput):
    """Hidden JSON input plus a JS photo picker and drawing surface (see static/js/land_plan_editor.js).

    ProjectForm fills in the per-instance config below before rendering.
    """
    slots = []        # [(field name, label), ...] of the photo fields that can be annotated
    images = {}       # field name -> {id, url, thumb, title} for photos already saved
    land_ids = []     # ids of the services the editor is enabled for
    endpoint = ''     # admin URL returning {id, url, thumb, title} for an image id (the id is the trailing 0)
    save_url = ''     # autosave endpoint for this project ('' until the project has been saved once)
    rev = 0           # revision the page was rendered at (optimistic concurrency)
    history = {}      # saved undo/redo stacks + last open photo

    class Media:
        css = {'all': ['css/land_plan.css']}
        js = ['js/land_plan_editor.js']

    def render(self, name, value, attrs=None, renderer=None):
        hidden = super().render(name, value, attrs, renderer)
        input_id = (attrs or {}).get('id') or f'id_{name}'
        return format_html(
            '{}<div class="lp-editor" data-input="{}" data-slots="{}" data-images="{}" data-land="{}" data-endpoint="{}" data-save-url="{}" data-rev="{}" data-history="{}"></div>',
            hidden, input_id, json.dumps(self.slots), json.dumps(self.images), json.dumps(self.land_ids), self.endpoint,
            self.save_url, self.rev, json.dumps(self.history),
        )
