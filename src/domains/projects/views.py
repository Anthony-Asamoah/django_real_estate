from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Max, Min, Q
from django.shortcuts import get_object_or_404, render
from wagtail.models import Site

from domains.employees.models import Employee
from domains.pages.models import BrandingSettings, ServiceDetailPage
from .models import ACTIVE_STATUSES, PAST_STATUSES, STATUS_CHOICES, Project


def _site_currency_symbol():
    site = Site.objects.filter(is_default_site=True).first()
    if site:
        branding = BrandingSettings.for_site(site)
        if branding and branding.default_currency_id:
            return branding.default_currency.symbol
    return 'GH₵'


def index(request):
    all_published = Project.objects.filter(is_published=True)
    qs = all_published.order_by('-project_date')

    # ── Quick filters ─────────────────────────────────────────────────────────
    status = request.GET.get('status', 'all')
    if status == 'past':
        qs = qs.filter(status__in=PAST_STATUSES)
    elif status == 'active':
        qs = qs.filter(status__in=ACTIVE_STATUSES)
    elif status in dict(STATUS_CHOICES):
        qs = qs.filter(status=status)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q))

    service_id = request.GET.get('service', '').strip()
    if service_id:
        qs = qs.filter(service_id=service_id)

    # ── Advanced filters ──────────────────────────────────────────────────────
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    sqft_min = request.GET.get('sqft_min', '').strip()
    sqft_max = request.GET.get('sqft_max', '').strip()
    bedrooms_min = request.GET.get('bedrooms_min', '').strip()
    city_filter = request.GET.get('city', '').strip()
    state_filter = request.GET.get('state', '').strip()
    emp_id = request.GET.get('employee', '').strip()

    if price_min:    qs = qs.filter(price__gte=price_min)
    if price_max:    qs = qs.filter(price__lte=price_max)
    if sqft_min:     qs = qs.filter(sqft__gte=sqft_min)
    if sqft_max:     qs = qs.filter(sqft__lte=sqft_max)
    if bedrooms_min: qs = qs.filter(bedrooms__gte=bedrooms_min)
    if city_filter:  qs = qs.filter(city__icontains=city_filter)
    if state_filter: qs = qs.filter(state_or_region__icontains=state_filter)
    if emp_id:       qs = qs.filter(employee_id=emp_id)

    # ── Sort ──────────────────────────────────────────────────────────────────
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'sqft_desc':
        qs = qs.order_by('-sqft')
    # default order is already -project_date

    # ── Active filter chips ───────────────────────────────────────────────────
    sym = _site_currency_symbol()
    filter_chips = []
    if price_min and price_max:
        filter_chips.append(
            {'label': f'Price: {sym}{int(price_min):,}–{sym}{int(price_max):,}', 'remove_keys': ['price_min', 'price_max']})
    elif price_min:
        filter_chips.append({'label': f'Price ≥ {sym}{int(price_min):,}', 'remove_keys': ['price_min']})
    elif price_max:
        filter_chips.append({'label': f'Price ≤ {sym}{int(price_max):,}', 'remove_keys': ['price_max']})
    if sqft_min and sqft_max:
        filter_chips.append(
            {'label': f'Sqft: {int(sqft_min):,}–{int(sqft_max):,}', 'remove_keys': ['sqft_min', 'sqft_max']})
    elif sqft_min:
        filter_chips.append({'label': f'Sqft ≥ {int(sqft_min):,}', 'remove_keys': ['sqft_min']})
    elif sqft_max:
        filter_chips.append({'label': f'Sqft ≤ {int(sqft_max):,}', 'remove_keys': ['sqft_max']})
    if bedrooms_min:
        filter_chips.append({'label': f'Bedrooms: {bedrooms_min}+', 'remove_keys': ['bedrooms_min']})
    if city_filter:
        filter_chips.append({'label': f'City: {city_filter}', 'remove_keys': ['city']})
    if state_filter:
        filter_chips.append({'label': f'Region: {state_filter}', 'remove_keys': ['state']})
    if emp_id:
        try:
            emp_name = Employee.objects.get(pk=emp_id).name
        except Employee.DoesNotExist:
            emp_name = 'Unknown'
        filter_chips.append({'label': f'Lead: {emp_name}', 'remove_keys': ['employee']})

    for chip in filter_chips:
        params = request.GET.copy()
        for key in chip['remove_keys']:
            params.pop(key, None)
        params.pop('page', None)
        chip['remove_url'] = '?' + params.urlencode() if params else '?'

    # Clear-all advanced filters — preserves quick-filter params only
    clear_params = {k: v for k, v in request.GET.items() if k in ('q', 'service', 'status', 'sort')}
    clear_url = '?' + urlencode(clear_params) if clear_params else '?'

    # Pagination base querystring (all current params minus page)
    page_params = request.GET.copy()
    page_params.pop('page', None)
    base_qs = page_params.urlencode()

    # ── Range hints for advanced filter inputs ────────────────────────────────
    price_agg = all_published.aggregate(min=Min('price'), max=Max('price'))
    sqft_agg = all_published.aggregate(min=Min('sqft'), max=Max('sqft'))

    # ── Context ───────────────────────────────────────────────────────────────
    service_pages = ServiceDetailPage.objects.live().order_by('title')
    employees = Employee.objects.order_by('name')
    total_count = all_published.count()
    paginator = Paginator(qs, 9)
    paged = paginator.get_page(request.GET.get('page'))

    return render(request, 'projects/projects.html', {
        'query': paged,
        'service_pages': service_pages,
        'employees': employees,
        'status_filter': status,
        'values': request.GET,
        'filter_chips': filter_chips,
        'advanced_filter_count': len(filter_chips),
        'clear_url': clear_url,
        'base_qs': base_qs,
        'bedrooms_range': range(1, 11),
        'total_count': total_count,
        'price_agg': price_agg,
        'sqft_agg': sqft_agg,
        'sort': sort,
        'bc_items': [{'title': 'Projects', 'url': ''}],
    })


def project(request, project_id):
    obj = get_object_or_404(Project, pk=project_id)
    photos = [p for p in [obj.photo_1, obj.photo_2, obj.photo_3, obj.photo_4, obj.photo_5, obj.photo_6] if p]

    from wagtail.models import Site
    site = Site.find_for_request(request)
    branding = BrandingSettings.for_site(site) if site else None

    related = []
    if branding and branding.project_show_related:
        count = max(1, min(branding.project_related_count, 6))
        qs = Project.objects.filter(is_published=True).exclude(pk=obj.pk).order_by('-project_date')
        if obj.service_id:
            qs = qs.filter(service_id=obj.service_id)
        related = list(qs[:count])

    return render(request, 'projects/project.html', {
        'project': obj,
        'photos': photos,
        'related_projects': related,
        'bc_items': [
            {'title': 'Projects', 'url': '/projects/'},
            {'title': obj.title, 'url': ''},
        ],
    })
