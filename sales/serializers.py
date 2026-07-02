from rest_framework import serializers
import uuid
from cars.models import ModerationStatus, Status
from rest_framework.exceptions import NotFound
from django.core.exceptions import ValidationError
from .models import Sale
from cars.models import Car
from django.db import transaction

class SaleRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            "id",
            "seller",
            "buyer",
            "car",
            "sale_date",
            "transaction_number",
            "sale_price",
            "payment_method",
        ]
        read_only_fields = [
            "id",
            "sale_date",
            "seller",
            "buyer",
            "car",
            "transaction_number",
            "sale_price"
        ]
    
    def validate_moderation_status(self, car):
        """
        Validates that the car moderation status is approved.
        """
        if car.moderation_status != ModerationStatus.APPROVED:
            raise serializers.ValidationError("Car is not approved.")
    
    def validate_car_status(self, car, buyer):
        """
        Validates that the car status is available.
        """
        if car.status == Status.SOLD:
            raise serializers.ValidationError("Sold cars cannot be purchased.")

        if car.status == Status.RESERVED and car.buyer != buyer:
            raise serializers.ValidationError("You are not authorized to purchase this car.")
    
    def get_transaction_number(self):
        """
        Generates a unique transaction number.
        """
        return uuid.uuid4().hex

    def get_car(self):
        """
        Returns the car from the context.
        """
        return self.context['car']

    def get_buyer(self):
        """
        Returns the buyer from the request user.
        """
        buyer = getattr(
            self.context['request'].user,
            'customer_profile',
            None
        )

        if buyer is None:
            raise NotFound("Buyer not found.")
            
        return buyer

    @transaction.atomic
    def create(self, validated_data):
        try:
            car = Car.objects.select_for_update().filter(is_deleted=False).get(id=self.get_car().id)
        except Car.DoesNotExist:
            raise NotFound("Car not found.")

        buyer = self.get_buyer()
        transaction_number = self.get_transaction_number()

        self.validate_moderation_status(car)
        self.validate_car_status(car, buyer)

        sale = Sale(
            seller=car.owner,
            buyer=buyer,
            car=car,
            sale_price=car.listing_price,
            transaction_number=transaction_number,
            payment_method=validated_data['payment_method'],
        )

        car.status = Status.SOLD
        car.buyer = buyer

        try:
            car.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        sale.save()
        car.save(update_fields=["status", "buyer"])
        
        return sale

class SaleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            "id",
            "seller",
            "buyer",
            "car",
            "sale_date",
            "transaction_number",
            "sale_price",
            "payment_method",
        ]
        read_only_fields = fields