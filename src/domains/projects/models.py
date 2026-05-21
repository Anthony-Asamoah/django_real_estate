import pendulum
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.views.snippets import SnippetViewSet

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

PAST_STATUSES = [STATUS_COMPLETED, STATUS_SOLD]
ACTIVE_STATUSES = [STATUS_AVAILABLE, STATUS_IN_PROGRESS]


class ProjectViewSet(SnippetViewSet):
    model = None
    icon = 'folder-open-inverse'
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
            ],
            heading='Photos',
        ),
    ]

    def __str__(self):
        return self.title

    class Meta:
        pass


ProjectViewSet.model = Project
