from datetime import date
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField

name_validator = RegexValidator(
    regex=r'^[A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ -]+$',
    message="Name can contain only letters."
)

def validate_birth_date(value):
    today = date.today()

    if value > today:
        raise ValidationError("Date cannot be in the future.")

    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("User has to be at least 18 years old.")

class Customers(models.Model):
    
    first_name = models.CharField(
        max_length=40,
          validators=[name_validator]
          )
    last_name = models.CharField(
        max_length=100,
          validators=[name_validator]
          )
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(
        region='PL',
          null=True,
            blank=True
            )
    address = models.TextField(validators=[MinLengthValidator(8)])
    date_of_birth = models.DateField(validators=[validate_birth_date])
    created_at = models.DateTimeField(auto_now_add=True) 
