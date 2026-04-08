from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils import timezone
from person.models import Customer, Employee
from cars.models import Car

##ServiceAppointment

def validate_appointment_schedule_date(value):
    if value < timezone.now():
        raise ValidationError("Appointment date cannot be in the past.")

    
class ServiceAppointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class ServiceType(models.TextChoices):
        OIL_CHANGE = "oil_change", "Oil change"
        TIRE_CHANGE = "tire_change", "Tire change"
        INSPECTION = "inspection", "Inspection"
        BRAKE_SERVICE = "brake_service", "Brake service"
        DIAGNOSTICS = "diagnostics", "Diagnostics"
        BATTERY_REPLACEMENT = "battery_replacement", "Battery replacement"
        OTHER = "other", "Other"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="service_appointments"
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="service_appointments"
    )

    appointment_date = models.DateTimeField(
        validators=[validate_appointment_schedule_date]
    )

    service_type = models.CharField(
        max_length=30,
        choices=ServiceType.choices
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    notes = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(1500)]
        )
    
    created_at = models.DateTimeField(
        auto_now_add=True
        )

    def __str__(self):
        return f"{self.customer} - {self.service_type} ({self.appointment_date.date()})"


### TestDrive

class TestDrive(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="test_drives"
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="test_drives"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="test_drives"
    )

    scheduled_date = models.DateTimeField(
        validators=[validate_appointment_schedule_date]
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    notes = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(1500)]
        )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.car} ({self.scheduled_date.date()})"