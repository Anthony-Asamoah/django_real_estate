from wagtail.blocks import (
    StructBlock,
    CharBlock,
    TextBlock,
    ListBlock,
    RichTextBlock,
    StreamBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class ServiceCardBlock(StructBlock):
    icon = CharBlock(help_text='Font Awesome icon class, e.g. fa-home')
    title = CharBlock()
    body = TextBlock()

    class Meta:
        icon = 'list-ul'
        label = 'Service Card'
        template = 'blocks/service_card.html'


class ServicesRowBlock(StructBlock):
    heading = CharBlock(required=False)
    services = ListBlock(ServiceCardBlock())

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


class HeroBannerBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    image = ImageChooserBlock(required=False, help_text='Override the default hero background image')

    class Meta:
        icon = 'title'
        label = 'Page Hero Banner'
        template = 'blocks/hero_banner.html'


class CTABannerBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    button_text = CharBlock(required=False)
    button_url = CharBlock(required=False, help_text='Relative (/contact/) or absolute (https://...) URL')

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


class StatItemBlock(StructBlock):
    value = CharBlock(help_text='e.g. 200+')
    label = CharBlock(help_text='e.g. Projects Completed')
    icon = CharBlock(required=False, help_text='FA icon class, e.g. fa-home')


class StatsRowBlock(StructBlock):
    heading = CharBlock(required=False)
    stats = ListBlock(StatItemBlock())

    class Meta:
        icon = 'pick'
        label = 'Stats Row'
        template = 'blocks/stats_row.html'


class TestimonialsBlock(StructBlock):
    heading = CharBlock(required=False)

    class Meta:
        icon = 'openquote'
        label = 'Testimonials'
        template = 'blocks/testimonials.html'


class HomePageStreamBlock(StreamBlock):
    hero = HeroBlock()
    services_row = ServicesRowBlock()
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()


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
        from domains.realtors.models import realtor as Realtor
        context['mvp_realtor'] = Realtor.objects.filter(is_mvp=True).first()
        return context


class MVPRealtorBlock(StructBlock):
    heading = CharBlock(default='Seller Of The Month', required=False)

    class Meta:
        icon = 'user'
        label = 'MVP Realtor'
        template = 'blocks/mvp_realtor.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.realtors.models import realtor as Realtor
        context['mvp_realtor'] = Realtor.objects.filter(is_mvp=True).first()
        return context


class TeamSectionBlock(StructBlock):
    heading = CharBlock(default='Our Team', required=False)

    class Meta:
        icon = 'group'
        label = 'Team Section'
        template = 'blocks/team_section.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from domains.realtors.models import realtor as Realtor
        context['realtors'] = Realtor.objects.order_by('hire_date')
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


class ServicesIndexStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()
    cta_banner = CTABannerBlock()


class ServiceDetailStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    process_steps = ProcessStepsBlock()
    gallery = GalleryBlock()
    stats_row = StatsRowBlock()
    testimonials = TestimonialsBlock()
    cta_banner = CTABannerBlock()


class ProjectsIndexStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()


class ProjectDetailStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
    gallery = GalleryBlock()
    cta_banner = CTABannerBlock()


class ContactPageStreamBlock(StreamBlock):
    hero_banner = HeroBannerBlock()
    rich_text = RichTextBlock()
