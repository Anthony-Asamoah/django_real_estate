from django.db import models
from datetime import datetime

# Create your models here.


class realtor(models.Model):
	name = models.CharField(max_length=200, default='')
	description = models.TextField(blank=True)
	email = models.CharField(max_length=100, default='')
	phone = models.CharField(max_length=20, default='')
	is_mvp = models.BooleanField(default=False)
	hire_date = models.DateTimeField(default=datetime.now(), blank=True)
	photo = models.ImageField(upload_to='media/%Y/%m/%d/')

	def __str__(self):
		return self.name
