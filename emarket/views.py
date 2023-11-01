import random

from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse

from .models import Dealership, CarType, Car, Order, Client, OrderQuantity, Licence


def generate_plate():
    regions = (
        "АК",
        "КК",
        "АА",
        "КА",
        "АВ",
        "КВ",
        "АС",
        "КС",
        "АЕ",
        "КЕ",
        "АН",
        "КН",
        "АІ",
        "КІ",
        "АМ",
        "КМ",
        "АО",
        "КО",
        "АР",
        "КР",
        "АТ",
        "КТ",
        "АХ",
        "КХ",
        "ВА",
        "НА",
        "ВВ",
        "НВ",
        "ВС",
        "НС",
        "ВЕ",
        "НЕ",
        "ВН",
        "НН",
        "ВІ",
        "НІ",
        "ВК",
        "НК",
        "ВМ",
        "НМ",
        "ВО",
        "НО",
        "ВТ",
        "НТ",
        "ВХ",
        "НХ",
        "СА",
        "ІА",
        "СВ",
        "ІВ",
        "СЕ",
        "ІЕ",
        "СН",
        "ІН",
    )

    region_code = "".join(random.choice(regions) for _ in range(1))
    letters = "".join(random.choice("ABCEHKMOPTX") for _ in range(2))
    numbers = "".join(random.choice("0123456789") for _ in range(4))

    license_plate = f"{region_code} {numbers} {letters}"
    return license_plate


def get_cart():
    return Car.objects.filter(
        owner__isnull=True,
        blocked_by_order__client=Client.objects.first(),
    ).all()


def home_page(request):
    dealerships = Dealership.objects.all()
    return render(request, "home.html", {"dealerships": dealerships})


def car_types_page(request, pk):
    dealership = Dealership.objects.filter(id=pk).values("id", "name").first()

    car_types = list()
    for car_type in CarType.objects.filter(dealerships=pk).all():
        if Car.objects.filter(
            blocked_by_order__isnull=True, owner__isnull=True, car_type=car_type.id
        ).exists():
            car_types.append(car_type)

    return render(
        request,
        "emarket/car_types.html",
        {"dealership": dealership, "car_types": car_types},
    )


def cars_page(request, dealer_id, car_type_id):
    dealership = Dealership.objects.filter(id=dealer_id).values("name").first()
    car_type = CarType.objects.filter(id=car_type_id).values("name", "price").first()
    cars = Car.objects.filter(
        blocked_by_order__isnull=True, owner__isnull=True, car_type=car_type_id
    ).all()

    if not cars.exists():
        redirect_url = reverse("car_types_page", args=[dealer_id])
        return redirect(redirect_url)

    return render(
        request,
        "emarket/cars.html",
        {"dealership": dealership, "car_type": car_type, "cars": cars},
    )


def add_to_cart(request, pk):
    dealership = Dealership.objects.filter(available_car_types__car=pk).first()

    order, created = Order.objects.get_or_create(
        client=Client.objects.first(), dealership=dealership, is_paid=False
    )

    car_type = CarType.objects.filter(car=pk).first()
    OrderQuantity.objects.create(car_type=car_type, order=order)

    Car.objects.get(id=pk).block(order)

    redirect_url = reverse("cars_page", args=[dealership.id, car_type.id])
    return redirect(redirect_url)


def remove_from_cart(request, pk):
    dealership = Dealership.objects.filter(available_car_types__car=pk).first()

    order = Order.objects.filter(
        client=Client.objects.first(), dealership=dealership, is_paid=False
    ).first()

    car_type = CarType.objects.filter(car=pk).first()
    OrderQuantity.objects.delete(car_type=car_type, order=order)

    Car.objects.get(id=pk).unblock()

    redirect_url = reverse("cart_page")
    return redirect(redirect_url)


def cart_page(request):
    order_sum = 0
    for car in request.cart:
        order_sum += int(car.car_type.price)

    return render(
        request,
        "emarket/cart.html",
        {"order_sum": order_sum},
    )


def order_cancel(request):
    orders = Order.objects.filter(
        client=Client.objects.first(), is_paid=False
    ).all()

    # Тут можно було зробити одним запитом через Update
    for order in orders:
        cars = Car.objects.filter(owner__isnull=True, blocked_by_order=order).all()
        for car in cars:
            car.unblock()
        order.delete()

    return render(request, "emarket/order_cancel.html")


def order_pay(request):
    orders = Order.objects.filter(
        client=Client.objects.first(), is_paid=False
    ).all()

    cars_license = list()
    for order in orders:
        order.is_paid = True
        order.save()

        cars = Car.objects.filter(owner__isnull=True, blocked_by_order=order).all()
        for car in cars:
            car.sell()
            number = generate_plate()
            Licence.objects.create(car=car, number=number)
            cars_license.append({"car": car.car_type.name, "number": number})

    return render(request, "emarket/order_success.html", {"cars_license": cars_license})
