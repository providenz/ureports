from django.db.models import Q
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from django.contrib.auth import logout, login as dj_login, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator

from accounts.forms import (
    SignUpForm,
    ResetPasswordForm,
    ResetPasswordConfirmForm,
    ChangeUserInfoForm,
    LoginForm,
    UserManagementForm,
)
from accounts.send_mails import (
    send_activate_mail,
    send_reset_password_mail,
    send_change_email_mail,
)
from accounts.models import CustomUser as User


def login(request):
    if request.user.is_authenticated:
        return redirect("index")
    context = {}
    errors = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                get_username = User.objects.get(email=email)
                username = get_username.username
                is_active = get_username.is_active
            except User.DoesNotExist:
                is_active = True
                username = False
                errors["invald_email"] = "Invalid email credential!"
            if not is_active:
                errors["not_active"] = "This is not an activated email!"
            elif username:
                user = authenticate(request, username=username, password=password)
                if user:
                    dj_login(request, user)
                    return redirect("index")
                else:
                    errors["invalid_password"] = "Invalid password credential!"
    else:
        form = LoginForm()
    context["form"] = form
    context["errors"] = errors.values()
    return render(request, "accounts/login.html", context)


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("index")
    else:
        return redirect("index")


# Registration + Activations functions
def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    base_link = request.build_absolute_uri("/")
    errors = {}
    context = {}
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]
            re_password = form.cleaned_data["re_password"]
            try:
                check_email = User.objects.get(email=email)
            except User.DoesNotExist:
                check_email = False
            try:
                check_username = User.objects.get(username=username)
            except User.DoesNotExist:
                check_username = False
            if not check_email and not check_username:
                manager = User.objects
                if password == re_password:
                    try:
                        validate_password(password)
                        user = manager.create_user(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            password=password,
                        )
                        user.save()
                        send_activate_mail(base_link, user)
                        return redirect("activate_info")
                    except ValidationError as e:
                        errors["password_validation_error"] = e.messages[0]

                else:
                    errors[
                        "password_miss_match"
                    ] = "Password and Repeat Password miss match."
            else:
                if check_email:
                    errors["email_used"] = "Email already used."
                if check_username:
                    errors["username_used"] = "Username is already used."
    else:
        form = SignUpForm()
    context["form"] = form
    context["errors"] = errors.values()
    return render(request, "accounts/register.html", context)


def activate(request, uid, token):
    context = {}
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        context["user_not_exist"] = True
        return render(request, "accounts/activate.html", context)
    try:
        access = AccessToken(token)
        user.is_active = True
        user.save()
        context["activation_success"] = True
    except TokenError:
        if not user.is_active:
            user.delete()
            context["user_delete"] = True
        else:
            context["already_confirmed"] = True
    return render(request, "accounts/activate.html", context)


def activate_info(request):
    return render(request, "accounts/activate_info.html")


# Reset password functions
def reset_password(request):
    context = {}
    errors = {}
    base_link = request.build_absolute_uri("/")
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    send_reset_password_mail(base_link, user)
                    return redirect("reset_password_info")
                else:
                    errors["user_not_active"] = "Your account not activated"
                    form = SignUpForm()
            except User.DoesNotExist:
                errors["user_not_exist"] = "User with this email not exist"
    else:
        form = SignUpForm()

    context["form"] = form
    context["errors"] = errors.values()
    return render(request, "accounts/reset_password.html", context)


def reset_password_confirm(request, uid, token):
    context = {}
    errors = {}
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        errors["user_not_exist"] = True
        return render(request, "accounts/reset_password_confirm.html", context)
    try:
        access = AccessToken(token)
        if request.method == "POST":
            form = ResetPasswordConfirmForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data["password"]
                re_password = form.cleaned_data["re_password"]
                if password == re_password:
                    hashed_password = make_password(password)
                    user.password = hashed_password
                    user.save()
                    return redirect("reset_password_confirm_success")
                else:
                    errors[
                        "password_miss_match"
                    ] = "Password and Repeat Password miss match."
                    form = ResetPasswordConfirmForm()
                    context["form"] = form
        else:
            form = ResetPasswordConfirmForm()
            context["form"] = form
    except TokenError:
        errors["token_error"] = True
    context["errors"] = errors.values()
    return render(request, "accounts/reset_password_confirm.html", context)


def reset_password_info(request):
    return render(request, "accounts/reset_password_info.html")


def reset_password_confirm_success(request):
    if request.user.is_authenticated:
        logout(request)
    return render(request, "accounts/reset_password_confirm_success.html")


# prfile view for getting and changing profile info
@login_required
def profile(request):
    context = {}
    user = request.user
    if request.method == "POST":
        form = ChangeUserInfoForm(request.POST, request.FILES)
        if form.is_valid():
            for field_name, field_value in form.cleaned_data.items():
                if field_name != "logo":
                    if field_value:
                        setattr(user, field_name, field_value)
                        user.save()
            uploaded_image = request.FILES.get("logo")
            if uploaded_image:
                user.logo = uploaded_image
                user.save()
    else:
        initial_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }
        form = ChangeUserInfoForm(initial=initial_data)
    context["form"] = form
    return render(request, "accounts/profile.html", context)


# views for request and changing email
@login_required
def change_email(request):
    context = {}
    errors = {}
    user = request.user
    email = user.email
    base_link = request.build_absolute_uri("/")
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data["email"]
            try:
                check_email = User.objects.get(email=new_email)
            except User.DoesNotExist:
                check_email = False
            if not check_email:
                send_change_email_mail(base_link, user, new_email)
                return redirect("change_email_info")
            else:
                errors["email_used"] = "Email already used!"
    form = ResetPasswordForm()
    context["form"] = form
    context["errors"] = errors.values()
    return render(request, "accounts/change_email.html", context)


@login_required
def change_email_info(request):
    return render(request, "accounts/change_email_info.html")


def change_email_confirm(request, uid, token, email):
    context = {}
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        context["user_not_exist"] = True
        return render(request, "accounts/change_email_confirm.html", context)
    try:
        access = AccessToken(token)
        user.email = email
        user.save()
        if request.user.is_authenticated:
            logout(request)
        context["activation_success"] = True
    except TokenError:
        if not user.is_active:
            user.delete()
            context["user_delete"] = True
        else:
            context["already_confirmed"] = True
    return render(request, "accounts/change_email_confirm.html", context)


@login_required
def delete_account(request):
    request.user.delete()
    return redirect("login")


@user_passes_test(lambda u: u.is_superuser)
def manage_users(request):
    query = request.GET.get("q")
    if query:
        user_list = CustomUser.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).order_by("id")
    else:
        user_list = CustomUser.objects.all().order_by("-id")

    paginator = Paginator(user_list, 10)
    page = request.GET.get("page")
    users = paginator.get_page(page)

    return render(request, "accounts/manage_users.html", {"users": users})


from .models import CustomUser


def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.method == "POST":
        print(request.POST)
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("manage_users")
    else:
        form = UserManagementForm(instance=user)

    return HttpResponse(
        render_to_string(
            "partials/edit_user_form.html", {"form": form, "user_id": user_id}
        )
    )


from django.contrib import messages


def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user_email = user.email
    user.delete()
    messages.success(request, f'User {user_email} has been deleted.')
    return redirect("manage_users")
