from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
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
    get_orders,
    get_detail_orders,
)
from emarket.invoices import create_invoice, verify_signature
from emarket.models import Car, OrderInvoice
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
        if not Car.objects.filter(id=car_id, blocked_by_order_id=None).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

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
    def get(request):
        return Response(get_detail_orders(request), status=status.HTTP_200_OK)

    @staticmethod
    def post(request):
        orders = get_orders(request)
        full_url_webhook = request.build_absolute_uri(reverse("webhook-mono"))
        full_url_orders = request.build_absolute_uri(reverse("orders"))
        invoice_url = create_invoice(
            orders,
            full_url_webhook,
            full_url_orders,
        )
        return Response({"invoice_url": invoice_url}, status=status.HTTP_200_OK)

    @staticmethod
    def delete(request):
        cancel_order(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MonoAcquiringWebhookReceiver(APIView):
    @staticmethod
    def post(request):
        try:
            verify_signature(request)
        except Exception as e:
            return Response({"status": "error"}, status=400)
        reference = request.data.get("reference")
        order_invoice = OrderInvoice.objects.get(id=reference)
        if order_invoice.invoice_id != request.data.get("invoiceId"):
            return Response({"status": "error"}, status=400)

        _status = request.data.get("status", "error")
        order_invoice.status = _status
        order_invoice.save()

        if _status == "success":
            pay_order(request, order_invoice.orders.all())

        return Response({"status": "ok"})
