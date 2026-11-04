from django.urls import reverse
from wagtail.admin.forms import WagtailAdminModelForm


def image_info(image):
    """What the editor needs to show a photo: a full-width rendition and a small thumbnail."""
    return {
        'id': image.pk,
        'title': image.title,
        'url': image.get_rendition('width-1200').url,
        'thumb': image.get_rendition('fill-160x110').url,
    }


class ProjectForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import PHOTO_LABELS, PHOTO_SLOTS, land_plan_service_ids   # models imports this module
        project = self.instance
        widget = self.fields['land_plan_annotations'].widget
        widget.slots = [(s, PHOTO_LABELS[s]) for s in PHOTO_SLOTS]
        widget.land_ids = land_plan_service_ids()
        widget.endpoint = reverse('projects_image_info', args=[0])
        # Photos already saved are embedded; ones picked during this edit are fetched by the JS.
        widget.images = {s: image_info(getattr(project, s)) for s in PHOTO_SLOTS if project.pk and getattr(project, f'{s}_id')}
        # Autosave only exists for a saved project; a new one is saved with the normal form button first.
        widget.save_url = reverse('projects_land_plan_autosave', args=[project.pk]) if project.pk else ''
        widget.rev = project.land_plan_rev if project.pk else 0
        widget.history = project.land_plan_history if project.pk else {}
