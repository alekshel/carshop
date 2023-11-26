from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.signing import Signer, BadSignature
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import UserCreationFormWithEmail


def send_activation_email(request, user: User):
    user_signed = Signer().sign(user.id)
    signed_url = request.build_absolute_uri(f"/users/activate/{user_signed}")
    send_mail(
        "Registration complete",
        "Click here to activate your account: " + signed_url,
        "alek_shel@icloud.com",
        [user.email],
        fail_silently=False,
    )


class LoginViewCustom(LoginView):
    template_name = "users/login.html"


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("login")


def register(request):
    if request.method == "GET":
        form = UserCreationFormWithEmail()
        return render(request, "users/register.html", {"form": form})

    form = UserCreationFormWithEmail(request.POST)
    if form.is_valid():
        form.instance.is_active = False
        form.save()
        send_activation_email(request, form.instance)
        return redirect("login")
    return render(request, "users/register.html", {"form": form})


def activate(request, user_signed):
    try:
        user_id = Signer().unsign(user_signed)
    except BadSignature:
        return redirect("login")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("login")
    user.is_active = True
    user.save()
    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")
