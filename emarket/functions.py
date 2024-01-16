import random

from django.db.models import Count

from emarket.models import Dealership, CarType, Car, Order, OrderQuantity, Licence


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


def get_dealerships():
    return Dealership.objects.all()


def get_dealership(dealer_id):
    return Dealership.objects.get(id=dealer_id)


def get_car_types(dealer_id):
    return (
        CarType.objects.filter(
            dealerships=dealer_id,
            car__blocked_by_order__isnull=True,
            car__owner__isnull=True,
        )
        .annotate(count=Count("id"))
        .all()
    )


def get_car_type(car_type_id):
    return CarType.objects.filter(id=car_type_id).first()


def get_car_type_by_car(car_id):
    return CarType.objects.filter(car=car_id).first()


def get_cars(car_type_id):
    return Car.objects.filter(
        blocked_by_order__isnull=True, owner__isnull=True, car_type=car_type_id
    ).all()


def get_dealership_by_car(car_id):
    return Dealership.objects.filter(available_car_types__car=car_id).first()


def to_cart(request, car_id):
    dealership = get_dealership_by_car(car_id)

    order, created = Order.objects.get_or_create(
        client=request.user, dealership=dealership, is_paid=False
    )

    car_type = get_car_type_by_car(car_id)
    OrderQuantity.objects.create(car_type=car_type, order=order)

    Car.objects.get(id=car_id).block(order)

    return dealership.id, car_type.id


def from_cart(request, car_id):
    dealership = get_dealership_by_car(car_id)

    order = Order.objects.filter(
        client=request.user, dealership=dealership, is_paid=False
    ).first()

    car_type = get_car_type_by_car(car_id)
    OrderQuantity.objects.filter(car_type=car_type, order=order).delete()

    Car.objects.get(id=car_id).unblock()


def get_order_sum(cart):
    order_sum = 0
    for car in cart:
        order_sum += int(car.car_type.price)
    return order_sum


def get_orders(request):
    return Order.objects.filter(client=request.user, is_paid=False).all()


def blocked_cars(orders):
    return Car.objects.filter(owner__isnull=True, blocked_by_order__in=orders).all()


def cancel_order(request):
    orders = get_orders(request)

    cars_to_unblock = blocked_cars(orders)
    cars_to_unblock.update(blocked_by_order=None)

    Order.objects.filter(id__in=[order.id for order in orders]).delete()


def pay_order(request):
    orders = get_orders(request)

    cars_license = list()
    for car in blocked_cars(orders):
        car.sell()
        number = generate_plate()
        Licence.objects.create(car=car, number=number)
        cars_license.append({"car": car.car_type.name, "number": number})

    orders.update(is_paid=True)

    return cars_license
