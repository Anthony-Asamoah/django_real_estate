from django.contrib import admin
from listings.models import listing

# Register your models here.


@admin.register(listing)
class listingAdmin(admin.ModelAdmin):
	list_display = [
		'id',
		'is_published',
		'price',
		'address',
		'realtor',
		'city',
		'state_or_region',
		'zipcode',
		'listing_date',
	]

	list_display_links = [
		'id',
		'price',
	]

	list_filter = [
		'realtor',
		'price',
		'listing_date',
		'state_or_region'
	]

	list_editable = [
		'is_published'
	]

	search_fields = [
		'address',
		'realtor',
		'city',
		'state_or_region'
	]

	list_per_page = 20
