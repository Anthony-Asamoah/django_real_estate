from django.core.exceptions import ValidationError
from django.forms import CharField
from wagtail.blocks import (
    StructBlock,
    CharBlock,
    TextBlock,
    ListBlock,
    RichTextBlock,
    StreamBlock,
    ChoiceBlock,
    IntegerBlock,
    FieldBlock,
    StructBlockValidationError,
)
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock

from .widgets import IconInput


class IconCharBlock(FieldBlock):
    """CharBlock that renders a live Font Awesome icon preview in the Wagtail admin."""

    def __init__(self, required=True, help_text=None, **kwargs):
        self.field = CharField(
            required=required,
            help_text=help_text or 'Font Awesome icon class, e.g. fa-home',
            widget=IconInput(),
        )
        super().__init__(**kwargs)


class ServiceCardBlock(StructBlock):
    icon = IconCharBlock()
    title = CharBlock()
    body = TextBlock()

    class Meta:
        icon = 'list-ul'
        label = 'Service Card'
        template = 'blocks/service_card.html'


class ServicesRowBlock(StructBlock):
    heading = CharBlock(required=False)
    services = ListBlock(ServiceCardBlock())
    overlay_color = ChoiceBlock(
        choices=[
            ('black', 'Black'),
            ('brand-primary', 'Brand Primary'),
            ('brand-secondary', 'Brand Secondary'),
        ],
        default='brand-secondary',
        required=False,
        help_text='Tint colour of the overlay',
    )
    overlay_opacity = ChoiceBlock(
        choices=[
            ('0.3', 'Light (30%)'),
            ('0.5', 'Medium (50%)'),
            ('0.65', 'Dark (65%)'),
            ('0.85', 'Very Dark (85%)'),
        ],
        default='0.65',
        required=False,
        help_text='Opacity of the overlay',
    )

    class Meta:
        icon = 'list-ul'
        label = 'Services Row'
        template = 'blocks/services_row.html'


class HeroBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)

    class Meta:
        icon = 'title'
        label = 'Hero'
        template = 'blocks/hero.html'


class HeroSlideBlock(StructBlock):
    image = ImageChooserBlock(help_text='Background image for this slide')
    caption = CharBlock(required=False, help_text='Optional overlay caption')

    class Meta:
        icon = 'image'
        label = 'Slide'


class HeroSlideshowBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    slides = ListBlock(HeroSlideBlock(), min_num=3, help_text='Add at least 3 slides')
    overlay_color = ChoiceBlock(
        choices=[
            ('black', 'Black'),
            ('brand-primary', 'Brand Primary'),
            ('brand-secondary', 'Brand Secondary'),
        ],
        default='black',
        required=False,
        help_text='Tint colour of the overlay',
    )
    overlay_opacity = ChoiceBlock(
        choices=[
            ('0.3', 'Light (30%)'),
            ('0.5', 'Medium (50%)'),
            ('0.65', 'Dark (65%)'),
            ('0.85', 'Very Dark (85%)'),
        ],
        default='0.5',
        required=False,
        help_text='Opacity of the overlay',
    )
    transition_type = ChoiceBlock(
        choices=[('slide', 'Slide'), ('fade', 'Fade')],
        default='slide',
        help_text='Animation style between slides',
    )
    interval = IntegerBlock(
        default=5000,
        help_text='Milliseconds each slide is shown before transitioning (e.g. 5000 = 5s)',
    )
    animation_speed = IntegerBlock(
        default=600,
        help_text='Duration of the transition animation in milliseconds',
    )

    class Meta:
        icon = 'title'
        label = 'Hero Slideshow'
        template = 'blocks/hero_slideshow.html'


class HeroBannerBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    image = ImageChooserBlock(required=False, help_text='Override the default hero background image')
    overlay_color = ChoiceBlock(
        choices=[
            ('black', 'Black'),
            ('brand-primary', 'Brand Primary'),
            ('brand-secondary', 'Brand Secondary'),
        ],
        default='black',
        required=False,
        help_text='Tint colour of the overlay',
    )
    overlay_opacity = ChoiceBlock(
        choices=[
            ('0.3', 'Light (30%)'),
            ('0.5', 'Medium (50%)'),
            ('0.65', 'Dark (65%)'),
            ('0.85', 'Very Dark (85%)'),
        ],
        default='0.55',
        required=False,
        help_text='Opacity of the overlay',
    )

    class Meta:
        icon = 'title'
        label = 'Page Hero Banner'
        template = 'blocks/hero_banner.html'


class CTABannerBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    button_text = CharBlock(required=False)
    button_url = CharBlock(required=False, help_text='Relative (/contact/) or absolute (https://...) URL')
    button2_text = CharBlock(required=False, help_text='Secondary button label (optional)')
    button2_url = CharBlock(required=False, help_text='Secondary button URL (optional)')

    class Meta:
        icon = 'link'
        label = 'CTA Banner'
        template = 'blocks/cta_banner.html'


class ProcessStepBlock(StructBlock):
    step_number = CharBlock(help_text='e.g. 01, 02')
    title = CharBlock()
    body = TextBlock()


class ProcessStepsBlock(StructBlock):
    heading = CharBlock(required=False)
    steps = ListBlock(ProcessStepBlock())

    class Meta:
        icon = 'order'
        label = 'Process Steps'
        template = 'blocks/process_steps.html'


class GalleryImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = CharBlock(required=False)


class GalleryBlock(StructBlock):
    heading = CharBlock(required=False)
    images = ListBlock(GalleryImageBlock())

    class Meta:
        icon = 'image'
        label = 'Photo Gallery'
        template = 'blocks/gallery.html'


class VideoBlock(StructBlock):
    """A single video section that accepts EITHER an external embed
    (YouTube/Vimeo) or an uploaded video file.

    The embed is preferred when both are supplied. Embeds are recommended for
    poor/remote networks because the provider handles adaptive streaming.
    """

    heading = CharBlock(required=False)
    embed = EmbedBlock(
        required=False,
        label='Embed URL',
        help_text='Paste a YouTube/Vimeo (etc.) link. Best for poor networks — the '
                  'provider streams adaptively. Takes priority over an uploaded file.',
    )
    video_file = VideoChooserBlock(
        required=False,
        label='Uploaded video',
        help_text='Choose an uploaded video file. Used only when no embed URL is set.',
    )
    poster = ImageChooserBlock(
        required=False,
        help_text='Poster image shown before an uploaded video plays (optional). '
                  'Falls back to the file’s thumbnail if available.',
    )
    caption = CharBlock(required=False)

    class Meta:
        icon = 'media'
        label = 'Video'
        template = 'blocks/video.html'

    def clean(self, value):
        result = super().clean(value)
        if not result.get('embed') and not result.get('video_file'):
            raise StructBlockValidationError(
                block_errors={
                    'embed': ValidationError(
                        'Provide an embed URL or choose an uploaded video.'
                    ),
                }
            )
        return result


class StatItemBlock(StructBlock):
    value = CharBlock(help_text='e.g. 200+')
    label = CharBlock(help_text='e.g. Projects Completed')
    icon = IconCharBlock(required=False, help_text='Font Awesome icon class, e.g. fa-home')


class StatsRowBlock(StructBlock):
    heading = CharBlock(required=False)
    stats = ListBlock(StatItemBlock())

    class Meta:
        icon = 'pick'
        label = 'Stats Row'
        template = 'blocks/stats_row.html'


class TestimonialsBlock(StructBlock):
    heading = CharBlock(required=False)
    autoplay_delay = IntegerBlock(
        required=False,
        default=4500,
        help_text='Slide transition delay in milliseconds (e.g. 4500 = 4.5 s). Set to 0 to disable autoplay.',
        min_value=0,
        max_value=20000,
    )

    class Meta:
        icon = 'openquote'
        label = 'Testimonials'
        template = 'blocks/testimonials.html'


class HomePageStreamBlock(StreamBlock):
    hero = HeroBlock()
    hero_slideshow = HeroSlideshowBlock()
    services_row = ServicesRowBlock()
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()
    video = VideoBlock()


class AboutIntroBlock(StructBlock):
    heading = CharBlock(default='We Build More Than Structures')
    lead = CharBlock(required=False)
    image = ImageChooserBlock(required=False, help_text='Shown only when no MVP realtor is set')
    body = RichTextBlock(required=False)

    class Meta:
        icon = 'doc-full'
        label = 'About Intro'
        template = 'blocks/about_intro.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.employees.models import Employee
        context['mvp_realtor'] = Employee.objects.filter(is_featured=True).first()
        return context


class MVPRealtorBlock(StructBlock):
    heading = CharBlock(default='Featured Team Member', required=False)

    class Meta:
        icon = 'user'
        label = 'Featured Employee'
        template = 'blocks/mvp_realtor.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.employees.models import Employee
        context['mvp_realtor'] = Employee.objects.filter(is_featured=True).first()
        return context


class TeamSectionBlock(StructBlock):
    heading = CharBlock(default='Our Team', required=False)

    class Meta:
        icon = 'group'
        label = 'Team Section'
        template = 'blocks/team_section.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.employees.models import Employee
        context['employees'] = Employee.objects.order_by('hire_date')
        return context


class AboutPageStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    about_intro = AboutIntroBlock()
    mvp_realtor = MVPRealtorBlock()
    stats_row = StatsRowBlock()
    cta_banner = CTABannerBlock()
    team_section = TeamSectionBlock()
    testimonials = TestimonialsBlock()
    rich_text = RichTextBlock()
    video = VideoBlock()


class ServicesIndexStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()
    cta_banner = CTABannerBlock()


class ProjectsGridBlock(StructBlock):
    heading = CharBlock(required=False, default='Our Projects')
    empty_message = CharBlock(
        required=False,
        default='No projects in this category yet.',
        help_text='Shown when no published projects are linked to this service',
    )

    class Meta:
        icon = 'folder-open-inverse'
        label = 'Projects Grid'
        template = 'blocks/projects_grid.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.projects.models import ACTIVE_STATUSES, Project
        page = parent_context.get('page') if parent_context else None
        context['projects'] = (
            Project.objects.filter(
                service=page,
                is_published=True,
                status__in=ACTIVE_STATUSES,
            ).order_by('-project_date')
            if page else Project.objects.none()
        )
        return context


class ServiceDetailStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    process_steps = ProcessStepsBlock()
    gallery = GalleryBlock()
    projects_grid = ProjectsGridBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()
    cta_banner = CTABannerBlock()
    video = VideoBlock()


class ProjectsIndexStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()


class ProjectDetailStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    gallery = GalleryBlock()
    video = VideoBlock()
    cta_banner = CTABannerBlock()


class FAQItemBlock(StructBlock):
    question = CharBlock()
    answer = TextBlock()

    class Meta:
        icon = 'help'


class FAQBlock(StructBlock):
    heading = CharBlock(required=False, default='Frequently Asked Questions')
    items = ListBlock(FAQItemBlock())

    class Meta:
        icon = 'list-ul'
        template = 'blocks/faq.html'


class ContactPageStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    faq = FAQBlock()
