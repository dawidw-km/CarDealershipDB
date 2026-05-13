from rest_framework import serializers
from .models import Car

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "id",
            "owner",
            "brand",
            "model",
            "color",
            "vehicle_type",
            "year",
            "vin",
            "mileage",
            "purchase_price",
            "selling_price",
            "status",
            "description",
            "moderation_status",
            "reviewer",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "reviewer",
            "created_at"
        ]