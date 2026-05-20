from django.contrib import admin
from .models import Contact


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	list_display = ['listing', 'name', 'phone', 'email', 'phone', 'timestamp']

	list_display_links = ['listing', 'name', 'phone', 'email']

	search_fields = ['name', 'email', 'phone', 'message']

	list_per_page = 25
