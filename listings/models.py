from datetime import datetime

from django.db import models
from realtors.models import realtor

# Create your models here.


class Listing(models.Model):
	realtor = models.ForeignKey(realtor, on_delete=models.DO_NOTHING, default='')
	title = models.CharField(max_length=200, default='')
	address = models.CharField(max_length=200, default='')
	city = models.CharField(max_length=200, default='')
	state_or_region = models.CharField(max_length=200, default='')
	zipcode = models.CharField(max_length=11, default='')
	description = models.TextField(blank=True)
	price = models.IntegerField(default=0)
	bedrooms = models.IntegerField(default=1)
	bathrooms = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
	garage = models.IntegerField(default=0)
	sqft = models.IntegerField(default=0)
	lot_size = models.DecimalField(max_digits=10, decimal_places=1, default=1.0)
	is_published = models.BooleanField(default=True)
	listing_date = models.DateTimeField(blank=True, default=datetime.now())
	photo_main = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_1 = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_2 = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_3 = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_4 = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_5 = models.ImageField(upload_to='media/%Y/%M/%D/', blank=True)
	photo_6 = models.ImageField(upload_to='media/%Y/%m/%d/', blank=True)

	def __str__(self):
		return self.title
