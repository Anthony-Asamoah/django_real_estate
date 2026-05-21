import pendulum
from django.conf import settings as django_settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
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
        all_projects = self.get_children().live().specific().order_by('-first_published_at')
        paginator = Paginator(all_projects, 9)
        page_num = request.GET.get('page')
        try:
            projects = paginator.page(page_num)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)
        context['projects'] = projects
        context['paginator'] = paginator
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
    author_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
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
            FieldPanel('author_photo'),
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
    maps_url = models.URLField(
        blank=True,
        default=django_settings.MAPS_URL,
        help_text='Google Maps share link for your location (e.g. https://maps.app.goo.gl/…)',
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel('site_name'), FieldPanel('logo')],
            heading='Branding',
        ),
        MultiFieldPanel(
            [
                FieldPanel('primary_color', widget=ColorInput),
                FieldPanel('secondary_color', widget=ColorInput),
            ],
            heading='Colors',
        ),
        MultiFieldPanel(
            [FieldPanel('phone'), FieldPanel('email'), FieldPanel('maps_url')],
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
