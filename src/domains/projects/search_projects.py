from .models import Project


def search_result(GET):
    query = Project.objects.filter(is_published=True).order_by('-project_date')

    if GET.get('keywords'):
        query = query.filter(description__icontains=GET['keywords'])

    if GET.get('city'):
        query = query.filter(city__iexact=GET['city'])

    if GET.get('state'):
        query = query.filter(state_or_region__iexact=GET['state'].upper())

    if GET.get('bedrooms'):
        query = query.filter(bedrooms__lte=GET['bedrooms'])

    if GET.get('price'):
        query = query.filter(price__lte=GET['price'])

    return query
