from django.urls import path

from .views import (
    home_page,
    car_types_page,
    cars_page,
    add_to_cart,
    remove_from_cart,
    cart_page,
    order_pay,
    order_cancel,
    update_car_type,
    get_orders_page,
)

urlpatterns = [
    path("", home_page, name="home_page"),
    path("dealership-<int:pk>/", car_types_page, name="car_types_page"),
    path("update-car-type/", update_car_type, name="update_car_type"),
    path(
        "dealership-<int:dealer_id>/car-type-<int:car_type_id>/",
        cars_page,
        name="cars_page",
    ),
    path("cart/", cart_page, name="cart_page"),
    path("add-to-cart/<int:pk>/", add_to_cart),
    path("remove-from-cart/<int:pk>/", remove_from_cart),
    path("orders/", get_orders_page, name="orders"),
    path("order-pay/", order_pay),
    path("order-cancel/", order_cancel),
]
