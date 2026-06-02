from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Car, ModerationStatus, Status

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

        get_employee = getattr(
            self.context['request'].user,
            'employee_profile',
            None
        )

        if get_employee is None:
            raise serializers.ValidationError("You are not authorized to update the moderation status of this car.")
            
        instance.reviewer = get_employee
    
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


class BaseCarPurchaseStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Base serializer for updating the purchase status of a car.
    """

    TARGET_PURCHASE_STATUS = None

    class Meta:
        model = Car
        fields = [
            "id",
            "owner",
            "buyer",
            "status",

        ]

        read_only_fields = [
            "id",
            "owner",
            "buyer",
            "status",
        ]


    def validate_purchase(self, instance):
        """
        Validates that the purchase status is valid.
        """
        get_buyer = getattr(
            self.context['request'].user,
            'customer_profile',
            None
        )
        
        if instance.moderation_status != ModerationStatus.APPROVED:
            raise serializers.ValidationError("Car is not approved.")

        if instance.status == Status.SOLD:
            raise serializers.ValidationError("Sold cars cannot be purchased.")
        if instance.status == Status.RESERVED:
            if instance.buyer != get_buyer:
                raise serializers.ValidationError("You are not authorized to purchase this car.")
            else:
                return instance.status

    def update(self, instance, validated_data):
        self.validate_purchase(instance)

        buyer = getattr(
            self.context['request'].user,
            'customer_profile',
            None
        )

        if buyer is None:
            raise serializers.ValidationError("You are not authorized to update the purchase status of this car.")

        instance.status = self.TARGET_PURCHASE_STATUS
        instance.buyer = buyer

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save(
            update_fields=["status", "buyer"]
        )

        return instance

class CarPurchaseStatusUpdateSerializerSold(BaseCarPurchaseStatusUpdateSerializer):
    """
    Serializer for updating the purchase status of a car to sold by superuser or an employee.
    """
    TARGET_PURCHASE_STATUS = Status.SOLD


class CarPurchaseStatusUpdateSerializerReserved(BaseCarPurchaseStatusUpdateSerializer):
    """
    Serializer for updating the purchase status of a car to reserved by superuser or an employee.
    """
    TARGET_PURCHASE_STATUS = Status.RESERVED