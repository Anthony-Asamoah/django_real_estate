from wagtail.blocks import (
    StructBlock,
    CharBlock,
    TextBlock,
    ListBlock,
    RichTextBlock,
    URLBlock,
    StreamBlock,
)


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


class CTABannerBlock(StructBlock):
    heading = CharBlock()
    subtext = TextBlock(required=False)
    button_text = CharBlock(required=False)
    button_url = URLBlock(required=False)

    class Meta:
        icon = 'link'
        label = 'CTA Banner'
        template = 'blocks/cta_banner.html'


class HomePageStreamBlock(StreamBlock):
    hero = HeroBlock()
    services_row = ServicesRowBlock()
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()


class AboutPageStreamBlock(StreamBlock):
    rich_text = RichTextBlock()
    cta_banner = CTABannerBlock()
