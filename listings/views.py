from django.shortcuts import render


# Create your views here.

def index(request):
	return render(request, 'listings/listings.html', {'page_title': 'Listings'})


def listing(request):
	return render(request, 'listings/listing.html', {'page_title': 'Listing'})


def search(request):
	return render(request, 'listings/search.html', {'page_title': 'Search'})
