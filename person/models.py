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
    """
    Ensures that the birth date is not in the future and that the customer is at least 18 years old.
    """
    today = date.today()

    if value > today:
        raise ValidationError("Date cannot be in the future.")

    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("User has to be at least 18 years old.")
    
    
def validate_no_future_date(value):
    """
    Ensures that the date is not in the future.
    """
    if value > date.today():
        raise ValidationError("Date cannot be in the future.")


def validate_hire_date(value):
    validate_no_future_date(value)


class PersonBase(models.Model):
    """
    Abstract base model for common fields between Customer and Employee. Not intended to be used directly.
    """
    
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


    def clean(self):
        """
        Ensures that the user does not have an employee profile.
        """
        super().clean()
        if hasattr(self.user, 'employee_profile'):
            raise ValidationError(
                "This user already has an employee profile."
            )

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
        blank=True,
        validators=[validate_no_future_date]
    )

    hire_date = models.DateField(validators=[validate_hire_date])
    salary = models.DecimalField(
        max_digits=10,  
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Ensures that the employment status and layoff date are consistent.
        Ensures that the user does not have a customer profile.
        """
        super().clean()

        if (
            self.employment_status == self.EmploymentStatus.INACTIVE
            and self.layoff_date is None
        ):
            raise ValidationError(
                "Inactive employment status requires a layoff date."
            )
        if (
            self.employment_status == self.EmploymentStatus.ACTIVE
            and self.layoff_date is not None
        ):
            raise ValidationError(
                "Active employment status does not require a layoff date."
            )
        if hasattr(self.user, 'customer_profile'):
            raise ValidationError(
                "This user already has a customer profile."
            )
        
        

        