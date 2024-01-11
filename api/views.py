from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import ReadOnlyPermission
from api.serializers import DealershipSerializer, CarTypesSerializer, CarSerializer
from emarket.functions import (
    get_dealerships,
    get_car_types,
    get_cars,
    to_cart,
    from_cart,
    get_order_sum,
    cancel_order,
    pay_order,
)
from emarket.views import get_cart


class DealershipViewSet(viewsets.ModelViewSet):
    queryset = get_dealerships()
    serializer_class = DealershipSerializer
    permission_classes = [ReadOnlyPermission]


class CarTypesViewSet(viewsets.ModelViewSet):
    serializer_class = CarTypesSerializer
    permission_classes = [ReadOnlyPermission]

    def get_queryset(self):
        return get_car_types(self.kwargs["dealer_id"])


class CarsViewSet(viewsets.ModelViewSet):
    serializer_class = CarSerializer
    permission_classes = [ReadOnlyPermission]

    def get_queryset(self):
        return get_cars(self.kwargs["car_type_id"])


class CartView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @staticmethod
    def get(request):
        cart = get_cart(request)
        order_sum = get_order_sum(cart)
        serializer = CarSerializer(cart, many=True)

        return Response(
            {"order_sum": order_sum, "cars": serializer.data}, status=status.HTTP_200_OK
        )

    @staticmethod
    def post(request, car_id):
        dealer_id, car_type_id = to_cart(request, car_id)
        return Response(
            {"dealership_id": dealer_id, "car_type_id": car_type_id},
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete(request, car_id):
        from_cart(request, car_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        cars_license = pay_order(request)
        return Response(cars_license, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request):
        cancel_order(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
