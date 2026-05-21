from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from domains.employees.models import Employee
from domains.pages.models import ServiceDetailPage
from .models import ACTIVE_STATUSES, PAST_STATUSES, STATUS_CHOICES, Project


def index(request):
    qs = Project.objects.filter(is_published=True).order_by('-project_date')

    # ── Quick filters ─────────────────────────────────────────────────────────
    status = request.GET.get('status', 'past')
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

    # ── Active filter chips ───────────────────────────────────────────────────
    filter_chips = []
    if price_min and price_max:
        filter_chips.append(
            {'label': f'Price: ${int(price_min):,}–${int(price_max):,}', 'remove_keys': ['price_min', 'price_max']})
    elif price_min:
        filter_chips.append({'label': f'Price ≥ ${int(price_min):,}', 'remove_keys': ['price_min']})
    elif price_max:
        filter_chips.append({'label': f'Price ≤ ${int(price_max):,}', 'remove_keys': ['price_max']})
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
        filter_chips.append({'label': 'Project Lead: filtered', 'remove_keys': ['employee']})

    for chip in filter_chips:
        params = request.GET.copy()
        for key in chip['remove_keys']:
            params.pop(key, None)
        params.pop('page', None)
        chip['remove_url'] = '?' + params.urlencode() if params else '?'

    # Clear-all advanced filters — preserves quick-filter params only
    clear_params = {k: v for k, v in request.GET.items() if k in ('q', 'service', 'status')}
    clear_url = '?' + urlencode(clear_params) if clear_params else '?'

    # Pagination base querystring (all current params minus page)
    page_params = request.GET.copy()
    page_params.pop('page', None)
    base_qs = page_params.urlencode()

    # ── Context ───────────────────────────────────────────────────────────────
    service_pages = ServiceDetailPage.objects.live().order_by('title')
    employees = Employee.objects.order_by('name')
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
    })


def project(request, project_id):
    obj = get_object_or_404(Project, pk=project_id)
    photos = [p for p in [obj.photo_1, obj.photo_2, obj.photo_3, obj.photo_4, obj.photo_5, obj.photo_6] if p]
    return render(request, 'projects/project.html', {'project': obj, 'photos': photos})
