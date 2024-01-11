from rest_framework import serializers

from emarket.models import Dealership, CarType, Car


class DealershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealership
        fields = "__all__"


class CarTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = "__all__"


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"
