from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Listing

# Create your views here.


def index(request):
	query = Listing.objects.all().order_by('-listing_date').filter(is_published=True)

	paginator = Paginator(query, 6)
	page = request.GET.get('page')

	paged_listing = paginator.get_page(page)

	context = {
		'page_title': 'Listings',
		'query': paged_listing
	}
	return render(request, 'listings/listings.html', context)


def listing(request, listing_id):
	query = get_object_or_404(Listing, pk=listing_id)

	context = {
		'page_title': 'Listing',
		'listing': query
	}
	return render(request, 'listings/listing.html', context)


def search(request):
	return render(request, 'listings/search.html', {'page_title': 'Search'})
