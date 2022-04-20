from listings.models import Listing


def search_result(GET):
	query = Listing.objects.order_by('-listing_date').filter(is_published=True)

	# keywords
	if 'keywords' in GET:
		keywords = GET['keywords']
		if keywords:
			query = query.filter(description__icontains=keywords)

	# city
	if 'city' in GET:
		city = GET['city']
		if city:
			query = query.filter(city__iexact=city)

	# state_or_region
	if 'state' in GET:
		state = GET['state']
		if state:
			query = query.filter(state_or_region__iexact=state.upper())

	# bedrooms
	if 'bedrooms' in GET:
		bedrooms = GET['bedrooms']
		if bedrooms:
			query = query.filter(bedrooms__lte=bedrooms)

	# price
	if 'price' in GET:
		price = GET['price']
		if price:
			query = query.filter(price__lte=price)

	return query
