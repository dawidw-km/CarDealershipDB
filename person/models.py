from datetime import date
from django.conf import settings
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

class EmployeeRole(models.TextChoices):
        WORKER = 'worker', 'Worker'
        ADMIN = 'admin', 'Admin'

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

class Customer(PersonBase):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )

    address = models.TextField(validators=[MinLengthValidator(8)])
    date_of_birth = models.DateField(validators=[validate_birth_date])
    created_at = models.DateTimeField(auto_now_add=True)


class Employee(PersonBase):
    
    class EmployeeRole(models.TextChoices):
        WORKER = 'worker', 'Worker'
        ADMIN = 'admin', 'Admin'

    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )

    role = models.CharField(
        max_length=10,
        choices=EmployeeRole.choices,
        default=EmployeeRole.WORKER
    )

    employment_status = models.CharField(
        max_length=10,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )
    layoff_date = models.DateField(
        null=True,
        blank=True
    )

    hire_date = models.DateField(validators=[validate_hire_date])
    salary = models.DecimalField(
        max_digits=10,  
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    created_at = models.DateTimeField(auto_now_add=True)