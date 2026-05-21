import pendulum
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.snippets.models import register_snippet


@register_snippet
class ProjectInquiry(models.Model):
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
        db_table = 'contacts_contact'
        ordering = ['-timestamp']
        verbose_name = 'Project Inquiry'
        verbose_name_plural = 'Project Inquiries'


@register_snippet
class GeneralInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)
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
        db_table = 'contacts_generalinquiry'
        ordering = ['-timestamp']
        verbose_name = 'General Inquiry'
        verbose_name_plural = 'General Inquiries'


@register_setting
class EmailSettings(BaseSiteSetting):
    project_inquiry_subject = models.CharField(
        max_length=200,
        default='Thank you for your inquiry',
        help_text='Subject line for project inquiry confirmation emails',
    )
    project_inquiry_intro = models.TextField(
        default='Thank you for reaching out about {project}. We have received your inquiry and will be in touch shortly.',
        help_text='Intro paragraph. Use {project} to insert the project name.',
    )
    general_inquiry_subject = models.CharField(
        max_length=200,
        default='We received your message',
        help_text='Subject line for general contact form confirmation emails',
    )
    general_inquiry_intro = models.TextField(
        default='Thank you for contacting us, {name}. We have received your message and will be in touch shortly.',
        help_text='Intro paragraph. Use {name} to insert the sender\'s name.',
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel('project_inquiry_subject'), FieldPanel('project_inquiry_intro')],
            heading='Project Inquiry Email',
        ),
        MultiFieldPanel(
            [FieldPanel('general_inquiry_subject'), FieldPanel('general_inquiry_intro')],
            heading='General Inquiry Email',
        ),
    ]

    class Meta:
        verbose_name = 'Email Settings'
