from django.db import models
from django.core.validators import MaxLengthValidator
from person.models import Customer, Employee
from cars.models import Car

class Sale(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sales'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='sales'
    )

    sale_date = models.DateField()

    sale_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50)

    notes = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(1500)]
        )
    
    created_at = models.DateField(auto_now_add=True)