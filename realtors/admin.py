from django.contrib import admin
from realtors.models import realtor

# Register your models here.


@admin.register(realtor)
class realtorAdmin(admin.ModelAdmin):
	list_display = [
		'name',
		'hire_date',
		'phone',
		'email',
		'is_mvp'
	]

	list_display_links = [
		'name',
		'hire_date',
		'phone',
		'email'
	]

	list_editable = [
		'is_mvp'
	]

	search_fields = [
		'name',
		'phone',
		'email'
	]

	list_filter = [
		'is_mvp',
		'hire_date'
	]

	sortable_by = [
		'name',
		'hire_date',
		'is_mvp'
	]

	list_per_page = 20