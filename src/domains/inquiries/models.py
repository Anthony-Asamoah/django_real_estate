import pendulum
from django.db import models
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.rich_text import expand_db_html


class ReadOnlyPanel(FieldPanel):
    """A FieldPanel that is always read-only."""

    def __init__(self, *args, **kwargs):
        kwargs['read_only'] = True
        super().__init__(*args, **kwargs)


class ReadOnlyRichTextPanel(ReadOnlyPanel):
    """Read-only panel that renders RichTextField content as HTML.

    Wagtail's read-only output escapes the display value, and its default
    `format_value_for_display` only strips a `RichText` object down to plain
    text — a RichTextField's raw value is a `str`, so it falls through and the
    admin ends up showing literal `<p>` tags. Expanding the stored rich text
    and marking it safe renders the sender's formatting as they wrote it.
    """

    def format_value_for_display(self, value):
        return mark_safe(expand_db_html(value or ''))


class ProjectInquiry(models.Model):
    listing = models.CharField(max_length=200)
    listing_id = models.IntegerField()
    name = models.CharField(max_length=100, blank=False)
    phone = models.CharField(max_length=15, blank=False)
    email = models.CharField(max_length=100, blank=False)
    message = RichTextField(blank=True)
    timestamp = models.DateTimeField(default=pendulum.now)
    user_id = models.IntegerField(blank=False)
    is_read = models.BooleanField(default=False)

    panels = [
        MultiFieldPanel(
            [ReadOnlyPanel('listing'), ReadOnlyPanel('listing_id')],
            heading='Listing',
        ),
        MultiFieldPanel(
            [ReadOnlyPanel('name'), ReadOnlyPanel('email'), ReadOnlyPanel('phone')],
            heading='Contact Info',
        ),
        MultiFieldPanel(
            [
                ReadOnlyRichTextPanel('message'),
                ReadOnlyPanel('timestamp'),
                ReadOnlyPanel('user_id'),
                ReadOnlyPanel('is_read'),
            ],
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


class GeneralInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(
        max_length=200,
        blank=True,
        help_text='Service the person is interested in',
    )
    message = RichTextField(blank=True)
    timestamp = models.DateTimeField(default=pendulum.now)
    is_read = models.BooleanField(default=False)

    panels = [
        MultiFieldPanel(
            [ReadOnlyPanel('name'), ReadOnlyPanel('email'), ReadOnlyPanel('phone')],
            heading='Contact Info',
        ),
        MultiFieldPanel(
            [
                ReadOnlyPanel('service'),
                ReadOnlyRichTextPanel('message'),
                ReadOnlyPanel('timestamp'),
                ReadOnlyPanel('is_read'),
            ],
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
