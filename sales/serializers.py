from rest_framework import serializers
import uuid
from cars.models import ModerationStatus, Status
from .models import Sale

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
    
    def validate_moderation_status(self):
        """
        Validates that the car moderation status is approved.
        """
        if self.get_car().moderation_status != ModerationStatus.APPROVED:
            raise serializers.ValidationError("Car is not approved.")
    
    def validate_car_status(self):
        """
        Validates that the car status is available.
        """
        if self.get_car().status == Status.SOLD:
            raise serializers.ValidationError("Sold cars cannot be purchased.")

        if self.get_car().status == Status.RESERVED and self.get_car().buyer != self.get_buyer():
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
            raise serializers.ValidationError("Buyer not found.")
            
        return buyer

    def create(self, validated_data):

        self.validate_moderation_status()
        self.validate_car_status()

        buyer = self.get_buyer()
        car = self.get_car()
        transaction_number = self.get_transaction_number()

        sale = Sale(
            seller=car.owner,
            buyer=buyer,
            car=car,
            sale_price=car.listing_price,
            transaction_number=transaction_number,
            payment_method=validated_data['payment_method'],
        )
        sale.save()
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