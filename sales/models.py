from django.db import models
from person.models import Customer
from cars.models import Car

class Sale(models.Model):

    class PaymentMethod(models.TextChoices):
        CARD = 'card', 'Card'
        TRANSFER = 'transfer', 'Transfer'
        LEASING = 'leasing', 'Leasing'

    seller = models.ForeignKey(
        'person.Customer',
        on_delete=models.PROTECT,
        related_name='sold_cars_sales'
    )

    buyer = models.ForeignKey(
        'person.Customer',
        on_delete=models.PROTECT,
        related_name='bought_cars_sales'
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='sales'
    )

    sale_date = models.DateField(auto_now_add=True)
    transaction_number = models.CharField(max_length=32, unique=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices
        )
    