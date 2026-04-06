from datetime import date
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
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
    
def validate_hire_date(value):
    if value > date.today():
        raise ValidationError("Hire date cannot be in the future.")

class PersonBase(models.Model):
    
    first_name = models.CharField(
        max_length=40,
          validators=[name_validator]
          )
    last_name = models.CharField(
        max_length=100,
          validators=[name_validator]
          )
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(region='PL')

    class Meta:
        abstract = True

class Customers(PersonBase):

    address = models.TextField(validators=[MinLengthValidator(8)])
    date_of_birth = models.DateField(validators=[validate_birth_date])
    created_at = models.DateTimeField(auto_now_add=True)


class Employee(PersonBase):
    
    ROLE_CHOICES = [
        ('worker', 'Worker'),
        ('admin', 'Admin')
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='worker'
    )

    hire_date = models.DateField(validators=[validate_hire_date])
    salary = models.DecimalField(
        max_digits=10,  
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )