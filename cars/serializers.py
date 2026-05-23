from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Car, ModerationStatus

class CarRegistrationSerializer(serializers.ModelSerializer):
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
            "fuel_type",
            "transmission",
            "vehicle_condition",
            "accident_status",
            "listing_price",
            "description",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "owner",
        ]

    def create(self, validated_data):
        instance = Car(**validated_data)

        try:
            instance.full_clean(exclude=["owner", "reviewer"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance
    



class CarDetailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "id",
            "brand",
            "model",
            "color",
            "vehicle_type",
            "year",
            "vin",
            "mileage",
            "fuel_type",
            "transmission",
            "vehicle_condition",
            "accident_status",
            "listing_price",
            "description",
            "created_at"
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]

    CRITICAL_MODERATION_FIELDS = [
        "brand",
        "model",
        "year",
        "vin",
        "mileage",
        "fuel_type",
        "listing_price",
        "transmission",
        "vehicle_condition",
        "accident_status",
    ]
    
    def has_critical_moderation_fields_changed(self, instance, validated_data):
        """
        Checks if any of the critical moderation fields have been changed.
        """
        for field in validated_data:
            if field in self.CRITICAL_MODERATION_FIELDS:
                if validated_data[field] != getattr(instance, field):
                    return True
        return False

    def update_moderation_status(self, instance, validated_data):
        """
        Changes the moderation status of the car.
        """
        if self.has_critical_moderation_fields_changed(instance, validated_data):
            instance.moderation_status = ModerationStatus.PENDING
            instance.reviewer = None
        return instance

    def update(self, instance, validated_data):
        """
        Updates the car.
        """
        instance = self.update_moderation_status(instance, validated_data)

        instance.brand = validated_data.get('brand', instance.brand)
        instance.model = validated_data.get('model', instance.model)
        instance.color = validated_data.get('color', instance.color)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
        instance.year = validated_data.get('year', instance.year)
        instance.vin = validated_data.get('vin', instance.vin)
        instance.mileage = validated_data.get('mileage', instance.mileage)
        instance.fuel_type = validated_data.get('fuel_type', instance.fuel_type)
        instance.transmission = validated_data.get('transmission', instance.transmission)
        instance.vehicle_condition = validated_data.get('vehicle_condition', instance.vehicle_condition)
        instance.accident_status = validated_data.get('accident_status', instance.accident_status)
        instance.listing_price = validated_data.get('listing_price', instance.listing_price)
        instance.description = validated_data.get('description', instance.description)

        try:
            instance.full_clean(exclude=["owner", "reviewer"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance