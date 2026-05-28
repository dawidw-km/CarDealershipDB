from datetime import date
from django.db import models
from django.core.validators import RegexValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


vin_validator = RegexValidator(
        regex=r'^[A-HJ-NPR-Z0-9]{17}$',
        message='Invalid VIN format.'
        )

def car_year_validator(value):
    current_year = date.today().year
    if value < 1886:
        raise ValidationError("Year of production cannot be earlier than 1886.")
    if value > current_year:
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


class VehicleCondition(models.TextChoices):
    NEW = "new", "New"
    USED = "used", "Used"
    FOR_PARTS = "for_parts", "For parts"


class AccidentStatus(models.TextChoices):
    ACCIDENT_FREE = "accident_free", "Accident free"
    AFTER_IMPACT = "after_impact", "After impact"
    ACCIDENT_HISTORY = "accident_history", "Accident history"
    DAMAGED = "damaged", "Damaged"


class Status(models.TextChoices):
    AVAILABLE = "available", "Available"
    RESERVED = "reserved", "Reserved"
    SOLD = "sold", "Sold"


class ModerationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class FuelType(models.TextChoices):
    GASOLINE = "gasoline", "Gasoline"
    DIESEL = "diesel", "Diesel"
    ELECTRIC = "electric", "Electric"
    HYBRID = "hybrid", "Hybrid"
    PLUG_IN_HYBRID = "plug_in_hybrid", "Plug-in hybrid"
    OTHER = "other", "Other"


class Transmission(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTOMATIC = "automatic", "Automatic"
    SEMI_AUTOMATIC = "semi_automatic", "Semi-automatic"


class Car(models.Model):

    owner = models.ForeignKey(
        'person.Customer',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        related_name='cars'
    )

    brand = models.CharField(max_length=40, null=False, blank=False)
    model = models.CharField(max_length=40, null=False, blank=False)
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
            validators=[car_year_validator]
            )

    vin = models.CharField(max_length=17,
                           unique=True,
                           validators=[vin_validator]
                           )

    mileage = models.PositiveIntegerField(
            validators=[MaxValueValidator(2000000)]
            )

    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices, #type: ignore
        default=FuelType.GASOLINE,
    )

    transmission = models.CharField(
        max_length=20,
        choices=Transmission.choices, #type: ignore
        default=Transmission.MANUAL,
    )

    vehicle_condition = models.CharField(
        max_length=20,
        choices=VehicleCondition.choices, #type: ignore
        default=VehicleCondition.USED,
    )

    accident_status = models.CharField(
        max_length=20,
        choices=AccidentStatus.choices, #type: ignore
        default=AccidentStatus.ACCIDENT_FREE,
    )

    listing_price = models.DecimalField(
            max_digits=10,
            decimal_places=2,
            null=False,
            blank=False,
            validators=[MinValueValidator(1)]
            )

    status = models.CharField(
        max_length=10,
        choices=Status.choices, #type: ignore
        default=Status.AVAILABLE,
    )

    buyer = models.ForeignKey(
        'person.Customer',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='bought_cars'
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

    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        """
        Soft deletes the car.
        """
        self.is_deleted = True
        self.save()


    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


    def validate_new_vehicle(self):
        """
        Validates that a new vehicle is accident free and has mileage less than 100 km.
        """
        if (
            self.vehicle_condition == VehicleCondition.NEW
            and self.accident_status != AccidentStatus.ACCIDENT_FREE
        ):
            raise ValidationError(
                "New vehicle must be accident free."
                )

        if (
            self.vehicle_condition == VehicleCondition.NEW
            and self.mileage > 100
        ):
            raise ValidationError(
                "New vehicle cannot have mileage greater than 100 km"
                )

    def validate_sold_vehicle_rules(self):
        """
        Validates that a sold vehicle has a reviewer and a moderation status of approved.
        """
        if self.status != Status.SOLD:
            return

        if self.reviewer is None:
            raise ValidationError(
                "Sold vehicle must have a reviewer."
                )

        if self.moderation_status != ModerationStatus.APPROVED:
            raise ValidationError(
                "Sold vehicle must be approved."
                )

        if self.buyer is None:
            raise ValidationError(
                "Sold vehicle must have a buyer."
                )
        
        if self.buyer == self.owner:
            raise ValidationError(
                "Vehicle owner cannot buy their own vehicle."
                )

    def clean(self):

        super().clean()

        self.validate_new_vehicle()
        self.validate_sold_vehicle_rules()