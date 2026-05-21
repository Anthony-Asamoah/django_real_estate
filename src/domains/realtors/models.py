import os
import uuid

from django.db import models
import pendulum
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


def realtor_photo_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'realtors/{uuid.uuid4().hex}{ext}'


@register_snippet
class realtor(models.Model):
    name = models.CharField(max_length=200, default='')
    description = models.TextField(blank=True)
    email = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='')
    is_mvp = models.BooleanField(default=False)
    hire_date = models.DateTimeField(default=pendulum.now, blank=True)
    photo = models.ImageField(upload_to=realtor_photo_path)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('email'),
                FieldPanel('phone'),
                FieldPanel('photo'),
            ],
            heading='Basic Info',
        ),
        MultiFieldPanel(
            [
                FieldPanel('description'),
                FieldPanel('is_mvp'),
                FieldPanel('hire_date'),
            ],
            heading='Details',
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['hire_date']
