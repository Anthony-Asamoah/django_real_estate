from django.conf import settings as django_settings
from django.db import models
from wagtail.models import Page


def _default_site_name():
    return getattr(django_settings, 'SITE_NAME', 'Real Estate')
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from .blocks import HomePageStreamBlock, AboutPageStreamBlock


class HomePage(Page):
    body = StreamField(HomePageStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['pages.AboutPage']

    template = 'pages/home_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        from domains.listings.models import Listing
        from domains.listings.choices import price_choices, bedroom_choices, state_choices
        context['listing'] = Listing.objects.filter(
            is_published=True
        ).order_by('-listing_date')[:3]
        context['price_choices'] = price_choices
        context['bedroom_choices'] = bedroom_choices
        context['state_choices'] = state_choices
        return context

    class Meta:
        verbose_name = 'Home Page'


class AboutPage(Page):
    body = StreamField(AboutPageStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.HomePage']
    subpage_types = []

    template = 'pages/about_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        from domains.realtors.models import realtor as Realtor
        context['realtor'] = Realtor.objects.order_by('hire_date')
        context['mvp_realtor'] = Realtor.objects.filter(is_mvp=True).first()
        return context

    class Meta:
        verbose_name = 'About Page'


@register_setting
class BrandingSettings(BaseSiteSetting):
    site_name = models.CharField(
        max_length=100,
        default=_default_site_name,
        help_text='Displayed in browser title and footer',
    )
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Navbar logo image',
    )
    primary_color = models.CharField(
        max_length=7,
        default='#10284e',
        help_text='Hex color, e.g. #10284e',
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#30caa0',
        help_text='Hex color, e.g. #30caa0',
    )
    phone = models.CharField(max_length=20, blank=True, default='(617)-555-5555')
    email = models.EmailField(blank=True, default='info@site.co')
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    panels = [
        MultiFieldPanel(
            [FieldPanel('site_name'), FieldPanel('logo')],
            heading='Branding',
        ),
        MultiFieldPanel(
            [FieldPanel('primary_color'), FieldPanel('secondary_color')],
            heading='Colors',
        ),
        MultiFieldPanel(
            [FieldPanel('phone'), FieldPanel('email')],
            heading='Contact Info',
        ),
        MultiFieldPanel(
            [
                FieldPanel('twitter_url'),
                FieldPanel('facebook_url'),
                FieldPanel('linkedin_url'),
                FieldPanel('instagram_url'),
                FieldPanel('pinterest_url'),
                FieldPanel('tiktok_url'),
            ],
            heading='Social Links',
        ),
    ]

    class Meta:
        verbose_name = 'Branding & Site Settings'
