from django.urls import path
from rest_framework import routers
import rest_framework.authtoken.views
from . import views

router = routers.DefaultRouter()
router.register("dealerships", views.DealershipViewSet)
router.register(
    r"car_types/(?P<dealer_id>\d+)", views.CarTypesViewSet, basename="car_types"
)
router.register(r"cars/(?P<car_type_id>\d+)", views.CarsViewSet, basename="cars")

urlpatterns = router.urls
urlpatterns += [
    path("token/", rest_framework.authtoken.views.obtain_auth_token),
    path("cart/<int:car_id>/", views.CartView.as_view(), name="cart"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("order/", views.OrderView.as_view(), name="order"),
    path(
        "webhook-mono/",
        views.MonoAcquiringWebhookReceiver.as_view(),
        name="webhook-mono",
    ),
]
