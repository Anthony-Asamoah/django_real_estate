from django.shortcuts import render

from domains.employees.models import Employee
from domains.projects.choices import bedroom_choices, price_choices, state_choices
from domains.projects.models import Project


def index(request):
    query = Project.objects.filter(is_published=True).order_by('-project_date')[:3]

    context = {
        'page_title': 'Home',
        'projects': query,
        'price_choices': price_choices,
        'bedroom_choices': bedroom_choices,
        'state_choices': state_choices,
    }

    return render(request, 'pages/index.html', context)


def about(request):
    query = Employee.objects.order_by('hire_date')
    featured = query.filter(is_featured=True)

    context = {
        'page_title': 'About',
        'employees': query,
        'featured': featured,
    }

    return render(request, 'pages/about.html', context)
