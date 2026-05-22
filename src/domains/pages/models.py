import pendulum
from django.conf import settings as django_settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

from .blocks import (
    HomePageStreamBlock,
    AboutPageStreamBlock,
    ServicesIndexStreamBlock,
    ServiceDetailStreamBlock,
    ProjectsIndexStreamBlock,
    ProjectDetailStreamBlock,
    ContactPageStreamBlock,
)
from .panels import ColorHistoryPanel, ColorPresetsPanel, ColorSavePanel
from .widgets import ColorInput


def _default_site_name():
    return getattr(django_settings, 'SITE_NAME', 'Real Estate')


class HomePage(Page):
    body = StreamField(HomePageStreamBlock(), use_json_field=True, blank=True)
    show_featured_projects = models.BooleanField(
        default=True,
        help_text='Toggle the Featured Work section on the home page',
    )
    featured_projects_heading = models.CharField(
        max_length=100,
        default='Featured Work',
        blank=True,
        help_text='Heading for the Featured Work section',
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        MultiFieldPanel(
            [
                FieldPanel('show_featured_projects'),
                FieldPanel('featured_projects_heading'),
            ],
            heading='Featured Projects Section',
        ),
    ]

    parent_page_types = ['wagtailcore.Page']
    subpage_types = [
        'pages.AboutPage',
        'pages.ServicesIndexPage',
        'pages.ProjectsIndexPage',
        'pages.ContactPage',
    ]

    template = 'pages/home_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        from domains.projects.models import Project
        context['featured_projects'] = Project.objects.filter(
            is_published=True
        ).order_by('-project_date')[:3]
        context['service_pages'] = ServiceDetailPage.objects.live().public().order_by('title')
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

    class Meta:
        verbose_name = 'About Page'


class ServicesIndexPage(Page):
    body = StreamField(ServicesIndexStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.HomePage']
    subpage_types = ['pages.ServiceDetailPage']

    template = 'pages/services_index_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['services'] = self.get_children().live().specific()
        return context

    class Meta:
        verbose_name = 'Services Index Page'


class ServiceDetailPage(Page):
    body = StreamField(ServiceDetailStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.ServicesIndexPage']
    subpage_types = []

    template = 'pages/service_detail_page.html'

    class Meta:
        verbose_name = 'Service Page'


class ProjectsIndexPage(Page):
    body = StreamField(ProjectsIndexStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.HomePage']
    subpage_types = ['pages.ProjectDetailPage']

    template = 'pages/projects_index_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        from domains.projects.models import Project
        services = ServiceDetailPage.objects.live().public().order_by('title')
        services_with_projects = []
        for service in services:
            qs = Project.objects.filter(service=service, is_published=True).order_by('-project_date')
            if qs.exists():
                services_with_projects.append({'service': service, 'projects': qs})
        context['services_with_projects'] = services_with_projects
        return context

    class Meta:
        verbose_name = 'Projects Index Page'


class ProjectDetailPage(Page):
    service = models.ForeignKey(
        'pages.ServiceDetailPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projects',
    )
    location = models.CharField(max_length=200, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    body = StreamField(ProjectDetailStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('service'),
            FieldPanel('location'),
            FieldPanel('completion_date'),
            FieldPanel('cover_image'),
        ], heading='Project Details'),
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.ProjectsIndexPage']
    subpage_types = []

    template = 'pages/project_detail_page.html'

    class Meta:
        verbose_name = 'Project Page'


class ContactPage(Page):
    body = StreamField(ContactPageStreamBlock(), use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    parent_page_types = ['pages.HomePage']
    subpage_types = []

    template = 'pages/contact_page.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['service_pages'] = ServiceDetailPage.objects.live().order_by('title')
        return context

    class Meta:
        verbose_name = 'Contact Page'


@register_snippet
class Testimonial(models.Model):
    author_name = models.CharField(max_length=200)
    author_role = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    service = models.ForeignKey(
        'pages.ServiceDetailPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='testimonials',
        help_text='Leave blank to show on all service pages',
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=pendulum.now)

    panels = [
        MultiFieldPanel([
            FieldPanel('author_name'),
            FieldPanel('author_role'),
        ], heading='Author'),
        MultiFieldPanel([
            FieldPanel('body'),
            FieldPanel('service'),
            FieldPanel('is_featured'),
        ], heading='Content'),
    ]

    def __str__(self):
        return f'{self.author_name} — {self.author_role or "testimonial"}'

    class Meta:
        ordering = ['-created_at']


@register_snippet
class ColorPreset(models.Model):
    name = models.CharField(max_length=60)
    primary_color = models.CharField(max_length=7, default='#10284e', help_text='Hex color, e.g. #10284e')
    secondary_color = models.CharField(max_length=7, default='#30caa0', help_text='Hex color, e.g. #30caa0')

    panels = [
        FieldPanel('name'),
        FieldPanel('primary_color', widget=ColorInput),
        FieldPanel('secondary_color', widget=ColorInput),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Color Preset'
        ordering = ['name']


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
    maps_url = models.TextField(
        blank=True,
        default=django_settings.MAPS_URL,
        help_text='Google Maps share link — used for the "Get Directions" button (e.g. https://maps.app.goo.gl/…)',
    )
    maps_embed_url = models.TextField(
        blank=True,
        default=django_settings.MAPS_EMBED_URL,
        help_text='Google Maps embed URL for the iframe — get it from Google Maps → Share → Embed a map → copy the iframe src',
    )

    BREADCRUMB_STYLE_CHOICES = [
        ('bar', 'Context Bar — light strip below nav (default)'),
        ('overlay', 'Hero Overlay — dark band that flows into the hero'),
    ]
    breadcrumb_style = models.CharField(
        max_length=10,
        choices=BREADCRUMB_STYLE_CHOICES,
        default='bar',
        help_text='Controls how breadcrumbs are displayed on interior pages',
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel('site_name'), FieldPanel('logo')],
            heading='Branding',
        ),
        MultiFieldPanel(
            [
                ColorPresetsPanel(),
                FieldPanel('primary_color', widget=ColorInput),
                FieldPanel('secondary_color', widget=ColorInput),
                ColorSavePanel(),
                ColorHistoryPanel(),
            ],
            heading='Colors',
        ),
        MultiFieldPanel(
            [FieldPanel('phone'), FieldPanel('email'), FieldPanel('maps_url'), FieldPanel('maps_embed_url')],
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
        MultiFieldPanel(
            [FieldPanel('breadcrumb_style')],
            heading='Layout',
        ),
    ]

    class Meta:
        verbose_name = 'Branding & Site Settings'


class BrandingColorHistory(models.Model):
    branding = models.ForeignKey(
        BrandingSettings,
        on_delete=models.CASCADE,
        related_name='color_history',
    )
    primary_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']


@receiver(pre_save, sender=BrandingSettings)
def _stash_old_colors(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = BrandingSettings.objects.get(pk=instance.pk)
            instance._old_primary = old.primary_color
            instance._old_secondary = old.secondary_color
        except BrandingSettings.DoesNotExist:
            pass


@receiver(post_save, sender=BrandingSettings)
def _record_color_history(sender, instance, created, **kwargs):
    if created:
        return
    old_primary = getattr(instance, '_old_primary', None)
    old_secondary = getattr(instance, '_old_secondary', None)
    if old_primary is None:
        return
    if old_primary != instance.primary_color or old_secondary != instance.secondary_color:
        BrandingColorHistory.objects.create(
            branding=instance,
            primary_color=old_primary,
            secondary_color=old_secondary,
        )
        ids = list(
            BrandingColorHistory.objects.filter(branding=instance)
            .order_by('-changed_at')
            .values_list('id', flat=True)[20:]
        )
        if ids:
            BrandingColorHistory.objects.filter(id__in=ids).delete()
