from .views import get_cart


class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cart = get_cart()
        response = self.get_response(request)
        return response
