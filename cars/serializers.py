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
            instance.full_clean(exclude=["reviewer"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance
    

class CarDetailSerializer(serializers.ModelSerializer):
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
            "created_at",
            "moderation_status",
            "reviewer",
        ]

        read_only_fields = fields

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
            instance.full_clean(exclude=["reviewer"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance


class CarModerationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "id",
            "moderation_status",
            "reviewer",
            "created_at"
        ]

        read_only_fields = [
            "id",
            "created_at",
            "reviewer",
        ]
    
    def validate_moderation_status(self, value):
        """
        Validates moderation status if it's Rejected or Approved.
        """
        allowed_statuses = [
            ModerationStatus.REJECTED,
            ModerationStatus.APPROVED,
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError("Moderation status must be Rejected or Approved.")
        return value

    def update(self, instance, validated_data):
        """
        Updates the moderation status of the car.
        """
        instance.moderation_status = validated_data.get('moderation_status', instance.moderation_status)
        instance.reviewer = getattr(
            self.context['request'].user,
            'employee_profile',
            None
        )

        try:
            instance.full_clean(exclude=["owner", "reviewer"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance


class CarSoftDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer for soft deleting a car.
    """
    class Meta:
        model = Car
        fields = [
            "id",
            "is_deleted",
        ]

        read_only_fields = [
            "id",
            "is_deleted",
        ]

    def soft_delete(self, instance):
        """
        Soft deletes the car.
        """
        instance.is_deleted = True
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Updates the car.
        """
        instance = self.soft_delete(instance)
        return instance


class BaseModerationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Base serializer for updating the moderation status of a car.
    """

    TARGET_MODERATION_STATUS = None

    class Meta:
        model = Car
        fields = [
            "id",
            "moderation_status",
            "reviewer",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "reviewer",
            "moderation_status",
        ]
    
    def update(self, instance, validated_data):
        instance.moderation_status = self.TARGET_MODERATION_STATUS

        instance.reviewer = getattr(
            self.context['request'].user,
            'employee_profile',
            None
        )

        try:
            instance.full_clean(exclude=["owner"])
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save(
            update_fields=[
                "moderation_status",
                "reviewer",
            ]
        )
        return instance


class ModerationStatusUpdateSerializerApproved(BaseModerationStatusUpdateSerializer):
    """
    Serializer for updating the moderation status of a car to approved by superuser or an employee.
    """
    TARGET_MODERATION_STATUS = ModerationStatus.APPROVED


class ModerationStatusUpdateSerializerRejected(BaseModerationStatusUpdateSerializer):
    """
    Serializer for updating the moderation status of a car to rejected by superuser or an employee.
    """
    TARGET_MODERATION_STATUS = ModerationStatus.REJECTED

