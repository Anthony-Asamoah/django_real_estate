from django.db import models
import pendulum
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


@register_snippet
class Contact(models.Model):
    listing = models.CharField(max_length=200)
    listing_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)
    phone = models.CharField(max_length=15, blank=False)
    email = models.CharField(max_length=100, blank=False)
    message = models.TextField(blank=False)
    timestamp = models.DateTimeField(default=pendulum.now)
    user_id = models.IntegerField(blank=False)

    panels = [
        MultiFieldPanel(
            [FieldPanel('listing'), FieldPanel('listing_id')],
            heading='Listing',
        ),
        MultiFieldPanel(
            [FieldPanel('name'), FieldPanel('email'), FieldPanel('phone')],
            heading='Contact Info',
        ),
        MultiFieldPanel(
            [FieldPanel('message'), FieldPanel('timestamp'), FieldPanel('user_id')],
            heading='Details',
        ),
    ]

    def __str__(self):
        return f'{self.name} — {self.listing}'

    class Meta:
        ordering = ['-timestamp']


@register_snippet
class GeneralInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(
        max_length=200,
        blank=True,
        help_text='Service the person is interested in',
    )
    message = models.TextField()
    timestamp = models.DateTimeField(default=pendulum.now)

    panels = [
        MultiFieldPanel(
            [FieldPanel('name'), FieldPanel('email'), FieldPanel('phone')],
            heading='Contact Info',
        ),
        MultiFieldPanel(
            [FieldPanel('service'), FieldPanel('message'), FieldPanel('timestamp')],
            heading='Details',
        ),
    ]

    def __str__(self):
        return f'{self.name} — {self.service or "general"}'

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'General Inquiry'
        verbose_name_plural = 'General Inquiries'
