import os
import uuid

import pendulum
from django.conf import settings
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


def employee_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'employees/{uuid.uuid4().hex}{ext}'


@register_snippet
class Employee(models.Model):
    name = models.CharField(max_length=200, default='')
    role = models.CharField(max_length=100, blank=True, help_text='e.g. Project Manager, Site Engineer')
    description = models.TextField(blank=True)
    email = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    is_featured = models.BooleanField(
        default=False,
        help_text='Feature on About page and team highlights',
    )
    hire_date = models.DateTimeField(default=pendulum.now, blank=True)
    photo = models.ImageField(upload_to=employee_photo_path)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='employee_profile',
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('role'),
                FieldPanel('email'),
                FieldPanel('phone'),
                FieldPanel('photo'),
            ],
            heading='Basic Info',
        ),
        MultiFieldPanel(
            [
                FieldPanel('description'),
                FieldPanel('is_featured'),
                FieldPanel('hire_date'),
                FieldPanel('user'),
            ],
            heading='Details',
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['hire_date']
