from django.db import models
from django.contrib.auth.models import User

import datetime
from django.utils import timezone
# Create your models here.

class Search(models.Model):

	user = models.ForeignKey(User, on_delete=models.CASCADE) # models.CASCADE
	project_name = models.CharField(max_length=50)
	created = models.DateTimeField(default=timezone.now())

	def __str__(self):
		return self.project_name