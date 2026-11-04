import json

import pendulum
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.views.snippets import SnippetViewSet

from infrastructure.utils.list_filters import KeepListFiltersViewSetMixin
from infrastructure.utils.profanity import contains_profanity
from .forms import ProjectForm
from .widgets import LandPlanWidget

STATUS_AVAILABLE = 'available'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_COMPLETED = 'completed'
STATUS_SOLD = 'sold'

STATUS_CHOICES = [
    (STATUS_AVAILABLE, 'Available'),
    (STATUS_IN_PROGRESS, 'In Progress'),
    (STATUS_COMPLETED, 'Completed'),
    (STATUS_SOLD, 'Sold'),
]

PAST_STATUSES = [STATUS_SOLD, STATUS_COMPLETED]
ACTIVE_STATUSES = [STATUS_AVAILABLE, STATUS_IN_PROGRESS, STATUS_COMPLETED]


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    panels = [
        FieldPanel('code'),
        FieldPanel('name'),
        FieldPanel('symbol'),
    ]

    def __str__(self):
        return f'{self.code} — {self.name}'

    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['code']


class ProjectViewSet(KeepListFiltersViewSetMixin, SnippetViewSet):
    model = None
    icon = 'folder-open-inverse'
    add_to_admin_menu = True
    menu_label = 'Projects'
    list_display = ['title', 'status', 'city', 'state_or_region', 'price', 'is_published', 'project_date']
    list_filter = ['is_published', 'status', 'service', 'state_or_region', 'employee']
    search_fields = ['title', 'address', 'city']
    ordering = ['-project_date']


class Project(models.Model):
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        'pages.ServiceDetailPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='catalog_projects',
        help_text='Which service category this project belongs to',
    )
    title = models.CharField(max_length=200, default='')
    address = models.CharField(max_length=200, default='')
    city = models.CharField(max_length=200, default='')
    state_or_region = models.CharField(max_length=200, default='')
    zipcode = models.CharField(max_length=11, default='')
    description = models.TextField(blank=True)
    price = models.IntegerField(default=0, help_text='Contract value or sale price')
    currency = models.ForeignKey(
        'projects.Currency',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Leave blank to use the site default currency',
    )

    # Optional fields — relevant for house/building sales, not needed for infrastructure/borehole work
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    garage = models.IntegerField(null=True, blank=True)
    sqft = models.IntegerField(null=True, blank=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    land_area_sqft = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Total plot area in sqft (for land/infrastructure projects)',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )
    is_published = models.BooleanField(default=True)
    project_date = models.DateTimeField(
        blank=True,
        default=pendulum.now,
    )
    photo_main = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_1 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_2 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_3 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_4 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_5 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    photo_6 = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    # Boundary + pin drawn over ONE of the photo slots above (land services only). Shape: see _clean_annotations.
    land_plan_annotations = models.JSONField(default=dict, blank=True)
    # Autosave bookkeeping (never shown in forms): undo/redo history, and a revision for optimistic concurrency.
    land_plan_history = models.JSONField(default=dict, blank=True, editable=False)
    land_plan_rev = models.PositiveIntegerField(default=0, editable=False)

    base_form_class = ProjectForm

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('employee'),
                FieldPanel('service'),
                FieldPanel('status'),
                FieldPanel('is_published'),
                FieldPanel('project_date'),
            ],
            heading='Project Info',
        ),
        MultiFieldPanel(
            [
                FieldPanel('address'),
                FieldPanel('city'),
                FieldPanel('state_or_region'),
                FieldPanel('zipcode'),
            ],
            heading='Location',
        ),
        MultiFieldPanel(
            [
                FieldPanel('price'),
                FieldPanel('currency'),
                FieldPanel('bedrooms'),
                FieldPanel('bathrooms'),
                FieldPanel('garage'),
                FieldPanel('sqft'),
                FieldPanel('lot_size'),
                FieldPanel('land_area_sqft'),
                FieldPanel('description'),
            ],
            heading='Project Details',
        ),
        MultiFieldPanel(
            [
                FieldPanel('photo_main'),
                FieldPanel('photo_1'),
                FieldPanel('photo_2'),
                FieldPanel('photo_3'),
                FieldPanel('photo_4'),
                FieldPanel('photo_5'),
                FieldPanel('photo_6'),
                FieldPanel(
                    'land_plan_annotations', widget=LandPlanWidget,
                    heading='Annotate a photo (land only)',
                ),
            ],
            heading='Photos',
        ),
    ]

    @cached_property
    def is_land(self):
        return bool(self.service_id) and self.service_id in land_plan_service_ids()

    @cached_property
    def land_annotated_slots(self):
        """Photo slots that carry annotations and should be shown with their overlay (land only, photo still set)."""
        photos = (self.land_plan_annotations or {}).get('photos', {})
        if not photos:
            return []   # most projects: skip the service-settings lookup entirely
        return [s for s in PHOTO_SLOTS if self.is_land and s in photos and getattr(self, f'{s}_id')]

    def clean(self):
        super().clean()
        if not self.is_land:
            self.land_plan_annotations = {}   # annotations only apply to land projects
            return
        available = [s for s in PHOTO_SLOTS if getattr(self, f'{s}_id')]
        try:
            self.land_plan_annotations = _clean_annotations(self.land_plan_annotations or {}, available)
        except ValidationError as e:
            raise ValidationError({'land_plan_annotations': e.messages})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # A normal form save also changes the annotations, so bump the revision: a stale autosave from another
        # tab then gets a conflict instead of silently overwriting. F() keeps the bump atomic.
        type(self).objects.filter(pk=self.pk).update(land_plan_rev=models.F('land_plan_rev') + 1)

    @property
    def land_plan_overlays(self):
        """One template-ready overlay (photo, polygon, edge labels, pin) per annotated photo, in slot order."""
        photos = self.land_plan_annotations.get('photos', {}) if self.land_plan_annotations else {}
        return [dict(_overlay(photos[s]), slot=s, image=getattr(self, s), label=PHOTO_LABELS[s])
                for s in self.land_annotated_slots]

    @cached_property
    def card_overlay(self):
        """Overlay for listing cards: the first annotated photo (the main photo when it is one), or None.

        Cards show the photo with object-fit: cover in a 16:9 box, so `layer` is the rectangle (in % of the box)
        that the full uncropped photo occupies; the overlay is drawn inside it and lines up with the crop.
        """
        overlays = self.land_plan_overlays
        if not overlays:
            return None
        first, image = overlays[0], overlays[0]['image']
        ratio, box = image.width / image.height, 16 / 9
        if ratio > box:
            w = ratio / box * 100
            layer = {'left': -(w - 100) / 2, 'top': 0, 'width': w, 'height': 100}
        else:
            h = box / ratio * 100
            layer = {'left': 0, 'top': -(h - 100) / 2, 'width': 100, 'height': h}
        # Hover zoom scales the photo about the box centre; the overlay must pivot on the same point.
        layer['origin_x'] = (50 - layer['left']) / layer['width'] * 100
        layer['origin_y'] = (50 - layer['top']) / layer['height'] * 100
        return dict(first, layer={k: round(v, 3) for k, v in layer.items()})

    @property
    def effective_currency(self):
        if self.currency_id:
            return self.currency
        try:
            from wagtail.models import Site
            from domains.pages.models import BrandingSettings
            site = Site.objects.filter(is_default_site=True).first()
            if site:
                settings = BrandingSettings.for_site(site)
                if settings and settings.default_currency_id:
                    return settings.default_currency
        except Exception:
            pass
        return None

    def __str__(self):
        return self.title

    class Meta:
        pass


MAX_POINTS, MAX_PINS, MAX_LABEL, MAX_DIM = 50, 1, 50, 20
# Annotatable photo slots (the Project photo fields).
PHOTO_SLOTS = ['photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6']
PHOTO_LABELS = dict(zip(PHOTO_SLOTS, ['Main photo', 'Photo 1', 'Photo 2', 'Photo 3', 'Photo 4', 'Photo 5', 'Photo 6']))
PIN_MIN_SIZE, PIN_MAX_SIZE = 0.6, 2.0   # pin icon scale; 1.0 is the default size
MAX_HISTORY, MAX_HISTORY_ENTRY = 50, 60_000   # autosaved undo/redo: entries kept, and max size of one entry (chars)


def land_plan_service_ids():
    """Ids of the services an admin enabled under Settings > Branding & Site Settings > Land Plan Annotations."""
    from wagtail.models import Site
    from domains.pages.models import BrandingSettings
    site = Site.objects.filter(is_default_site=True).first()
    branding = BrandingSettings.for_site(site) if site else None
    return list(branding.land_plan_services.values_list('pk', flat=True)) if branding else []


# Allowed overlay colours; the editor JS has the same list. Anything else is rejected, so the value is safe in a style attribute.
PALETTE = {'#ffc107', '#dc3545', '#0d6efd', '#198754', '#6f42c1', '#fd7e14', '#ffffff', '#212529'}
DEFAULT_BOUNDARY_COLOR = '#ffc107'


def _coord(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1:
        raise ValidationError('Coordinates must be numbers between 0 and 1.')
    return float(v)


def _text(v, limit, what):
    v = v.strip() if isinstance(v, str) else ''
    if len(v) > limit:
        raise ValidationError(f'{what} must be at most {limit} characters.')
    if contains_profanity(v):
        raise ValidationError(f'{what} contains inappropriate language.')
    return v


def _size(v):
    if v in (None, ''):
        return 1.0
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not PIN_MIN_SIZE <= v <= PIN_MAX_SIZE:
        raise ValidationError(f'Pin size must be between {PIN_MIN_SIZE} and {PIN_MAX_SIZE}.')
    return round(float(v), 2)


def _color(v, default):
    if v in (None, ''):
        return default
    if v not in PALETTE:
        raise ValidationError('Unsupported colour.')
    return v


def _clean_one(data):
    """Validate one photo's annotations (boundary polygon + at most one pin)."""
    if not isinstance(data, dict):
        raise ValidationError('Invalid annotation data.')
    boundary, pins = data.get('boundary', []), data.get('pins', [])
    if not isinstance(boundary, list) or not isinstance(pins, list):
        raise ValidationError('Invalid annotation data.')
    if len(boundary) > MAX_POINTS or len(pins) > MAX_PINS:
        raise ValidationError(f'At most {MAX_POINTS} boundary points and {MAX_PINS} pin are allowed per photo.')
    try:
        return {
            'color': _color(data.get('color'), DEFAULT_BOUNDARY_COLOR),
            'boundary': [{'x': _coord(p['x']), 'y': _coord(p['y']), 'dim': _text(p.get('dim', ''), MAX_DIM, 'Dimension')}
                         for p in boundary],
            'pins': [{'x': _coord(p['x']), 'y': _coord(p['y']), 'label': _text(p.get('label', ''), MAX_LABEL, 'Pin label'),
                      'color': _color(p.get('color'), ''), 'size': _size(p.get('size'))}
                     for p in pins],
        }
    except (KeyError, TypeError, AttributeError):
        raise ValidationError('Invalid annotation data.')


def _clean_annotations(data, available_slots):
    """Validate untrusted JSON `{"photos": {slot: {...}}}` from the editor and return a normalised copy.

    `available_slots` are the photo slots that currently hold an image; annotations for any other slot are dropped.
    """
    if not isinstance(data, dict):
        raise ValidationError('Invalid annotation data.')
    photos = data.get('photos', {})
    if not isinstance(photos, dict):
        raise ValidationError('Invalid annotation data.')
    return {'photos': {slot: _clean_one(photos[slot]) for slot in PHOTO_SLOTS if slot in photos and slot in available_slots}}


def _clean_history(history):
    """Undo/redo is a convenience, so bad entries are dropped rather than failing the save."""
    def entries(v):
        out = []
        for e in (v if isinstance(v, list) else [])[-MAX_HISTORY:]:
            try:
                if isinstance(e, str) and len(e) <= MAX_HISTORY_ENTRY and isinstance(json.loads(e), dict):
                    out.append(e)
            except ValueError:
                pass
        return out
    history = history if isinstance(history, dict) else {}
    active = history.get('active')
    return {'undo': entries(history.get('undo')), 'redo': entries(history.get('redo')),
            'active': active if active in PHOTO_SLOTS else ''}


def _overlay(entry):
    """Polygon, edge-label positions (as %) and pin for one photo's cleaned annotations."""
    pts, pins = entry.get('boundary', []), entry.get('pins', [])
    n = len(pts)
    edges = []
    for i in range(n if n > 2 else n - 1):
        a, b = pts[i], pts[(i + 1) % n]
        if a['dim']:
            # Keep the chip inside the photo even when the edge runs along its border.
            edges.append({'x': min(max((a['x'] + b['x']) / 2 * 100, 5), 95), 'y': min(max((a['y'] + b['y']) / 2 * 100, 4), 96), 'dim': a['dim']})
    return {
        'color': entry.get('color', DEFAULT_BOUNDARY_COLOR),
        'points': ' '.join(f"{p['x']:.4f},{p['y']:.4f}" for p in pts) if n > 1 else '',
        'vertices': [{'x': p['x'] * 100, 'y': p['y'] * 100} for p in pts],
        'edges': edges,
        'pins': [{'x': p['x'] * 100, 'y': p['y'] * 100, 'label': p['label'], 'color': p.get('color', ''),
                 'size': f"{p.get('size', 1.0):.2f}"} for p in pins],   # a string, so templates never localise the decimal point
    }


ProjectViewSet.model = Project
