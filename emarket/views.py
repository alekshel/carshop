from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse

from .functions import (
    get_dealerships,
    get_dealership,
    get_car_types,
    get_car_type,
    get_cars,
    to_cart,
    from_cart,
    get_order_sum,
    cancel_order,
    get_orders,
    get_detail_orders,
)
from .invoices import create_invoice
from .models import CarType, Car


def update_car_type(request):
    if not request.method == "POST":
        raise Exception("Method not allowed")

    car_type_id = request.POST.get("car_type_id")
    car_type = CarType.objects.filter(id=car_type_id).first()
    if not car_type:
        raise Exception("Car type not found")

    photo = request.FILES.get("photo")
    if photo:
        car_type.photo = photo
        car_type.save()

    dealer_id = car_type.dealerships.first().id
    redirect_url = reverse("car_types_page", args=[dealer_id])
    return redirect(redirect_url)


def get_cart(request):
    if request.user.is_anonymous:
        return []

    return Car.objects.filter(
        owner__isnull=True,
        blocked_by_order__client=request.user,
    ).all()


def home_page(request):
    dealerships = get_dealerships()
    return render(request, "home.html", {"dealerships": dealerships})


def car_types_page(request, pk):
    dealership = get_dealership(pk)
    car_types = get_car_types(pk)

    return render(
        request,
        "emarket/car_types.html",
        {"dealership": dealership, "car_types": car_types},
    )


def cars_page(request, dealer_id, car_type_id):
    dealership = get_dealership(dealer_id)
    car_type = get_car_type(car_type_id)
    cars = get_cars(car_type_id)

    if not cars.exists():
        redirect_url = reverse("car_types_page", args=[dealer_id])
        return redirect(redirect_url)

    return render(
        request,
        "emarket/cars.html",
        {"dealership": dealership, "car_type": car_type, "cars": cars},
    )


@login_required
def add_to_cart(request, pk):
    dealer_id, car_type_id = to_cart(request, pk)
    redirect_url = reverse("cars_page", args=[dealer_id, car_type_id])
    return redirect(redirect_url)


@login_required
def remove_from_cart(request, pk):
    from_cart(request, pk)
    redirect_url = reverse("cart_page")
    return redirect(redirect_url)


def cart_page(request):
    order_sum = get_order_sum(request.cart)

    return render(
        request,
        "emarket/cart.html",
        {"order_sum": order_sum},
    )


@login_required
def order_cancel(request):
    cancel_order(request)
    return render(request, "emarket/order_cancel.html")


@login_required
def order_pay(request):
    orders = get_orders(request)
    full_url_webhook = request.build_absolute_uri(reverse("webhook-mono"))
    full_url_orders = request.build_absolute_uri(reverse("orders"))
    invoice_url = create_invoice(orders, full_url_webhook, full_url_orders)

    return redirect(invoice_url)


@login_required
def get_orders_page(request):
    return render(
        request, "emarket/orders.html", {"orders": get_detail_orders(request)}
    )
