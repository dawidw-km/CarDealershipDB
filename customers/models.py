from django.db import models


class Customers(models.Model):
    
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=100)

