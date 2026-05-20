from django.db import models
import pendulum

# Create your models here.


class Contact(models.Model):
	listing = models.CharField(max_length=200)
	listing_id = models.IntegerField()
	name = models.CharField(max_length=100, blank=False)
	phone = models.CharField(max_length=15, blank=False)
	email = models.CharField(max_length=100, blank=False)
	message = models.TextField(blank=False)
	timestamp = models.DateTimeField(default=pendulum.now)
	user_id = models.IntegerField(blank=False)

	def __str__(self):
		return f"{self.name}, {self.timestamp}"
