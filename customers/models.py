from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class Customers(models.Model):
    
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region='PL', null=True, blank=True)
    address = models.TextField()
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)