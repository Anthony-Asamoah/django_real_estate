from django.shortcuts import render, HttpResponse
from listings.models import Listing
from realtors.models import realtor

# Create your views here.


def index(request):
	query = Listing.objects.all().order_by('-listing_date').filter(is_published=True)[:3]

	context = {
		'page_title': 'Home',
		'listing': query
	}

	return render(request, 'pages/index.html', context)


def about(request):
	query = realtor.objects.order_by('hire_date')
	mvp = query.filter(is_mvp=True)

	context = {
		'page_title': 'About',
		'realtor': query,
		'mvp': mvp
	}

	return render(request, 'pages/about.html', context)
