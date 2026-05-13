from datetime import datetime
from django.db import models
from django.core.validators import RegexValidator, MaxLengthValidator, MaxValueValidator
from django.core.exceptions import ValidationError


vin_validator = RegexValidator(
        regex=r'^[A-HJ-NPR-Z0-9]{17}$',
        message='Invalid VIN format.'
        )

def year_validator(year):
    current_year = datetime.now().year
    if year < 1886:
        raise ValidationError("Year of production cannot be earlier than 1886.")
    if year > current_year:
        raise ValidationError("Date of production cannot be in the future.")

class VehicleType(models.TextChoices):
    SEDAN = "sedan", "Sedan"
    HATCHBACK = "hatchback", "Hatchback"
    SUV = "suv", "SUV"
    COUPE = "coupe", "Coupe"
    WAGON = "wagon", "Wagon"
    CONVERTIBLE = "convertible", "Convertible"
    VAN = "van", "Van"
    PICKUP = "pickup", "Pickup"


class Status(models.TextChoices):
    AVAILABLE = "available", "Available"
    RESERVED = "reserved", "Reserved"
    SOLD = "sold", "Sold"

class ModerationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class Car(models.Model):

    owner = models.ForeignKey(
        'person.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cars'
    )

    brand = models.CharField(max_length=40)
    model = models.CharField(max_length=40)
    color = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices, #type: ignore
        blank=True
        )
    year = models.PositiveIntegerField(
            validators=[year_validator]
            )

    vin = models.CharField(max_length=17,
                           unique=True,
                           validators=[vin_validator]
                           )

    mileage = models.PositiveIntegerField(
            validators=[MaxValueValidator(2000000)]
            )

    purchase_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            null=True,
            blank=True
            )
    selling_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            null=True,
            blank=True
            )

    status = models.CharField(
        max_length=10,
        choices=Status.choices, #type: ignore
        default=Status.AVAILABLE,
    )

    description = models.TextField(
            blank=True,
            validators=[MaxLengthValidator(500)]
            )

    moderation_status = models.CharField(
        max_length=10,
        choices=ModerationStatus.choices, #type: ignore
        default=ModerationStatus.PENDING,
    )

    reviewer = models.ForeignKey(
        'person.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_cars'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"
