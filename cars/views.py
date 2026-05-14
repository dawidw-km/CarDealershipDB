from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from cars.models import Car
from cars.serializers import CarSerializer

@extend_schema(tags=["Cars"])
class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer