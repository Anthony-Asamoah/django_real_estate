from django import template

register = template.Library()


@register.simple_tag
def get_testimonials():
    from domains.pages.models import Testimonial
    return Testimonial.objects.filter(is_featured=True)


@register.simple_tag
def get_service_pages():
    from domains.pages.models import ServicesIndexPage
    services_index = ServicesIndexPage.objects.live().first()
    if services_index:
        return services_index.get_children().live().specific()
    return []
