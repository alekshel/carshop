from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path

from .views import register, activate, logout_view, ResetPasswordView, LoginViewCustom

urlpatterns = [
    path("login/", LoginViewCustom.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("forgot_password/", ResetPasswordView.as_view(), name="password_reset"),
    path(
        "forgot_password/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/users/login/",
        ),
        name="password_reset_confirm",
    ),
    path("register/", register, name="register"),
    path("activate/<user_signed>", activate, name="activate"),
]
