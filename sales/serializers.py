from rest_framework import serializers
import uuid
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
        