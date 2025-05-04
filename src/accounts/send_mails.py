from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone


def send_activate_mail(base_link, user):
    token = str(AccessToken.for_user(user))

    verification_link = f"{base_link}/activate/{user.id}/{token}"
    subject = "Email Activation"
    message = render_to_string(
        "accounts/activation_mail.html",
        {
            "user": user,
            "verification_link": verification_link,
        },
    )
    email = user.email
    plain_message = strip_tags(message)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email="u-saved-test@ukr.net",
        recipient_list=[
            email,
        ],
        html_message=message,
    )


def send_reset_password_mail(base_link, user):
    token = str(AccessToken.for_user(user))

    reset_password_link = f"{base_link}/reset_password_confirm/{user.id}/{token}"
    subject = "Reset Password"
    message = render_to_string(
        "accounts/reset_password_mail.html",
        {
            "user": user,
            "reset_password_link": reset_password_link,
        },
    )
    email = user.email
    plain_message = strip_tags(message)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email="u-saved-test@ukr.net",
        recipient_list=[
            email,
        ],
        html_message=message,
    )


def send_change_email_mail(base_link, user, new_email):
    token = str(AccessToken.for_user(user))
    verification_link = (
        f"{base_link}/change_email_confirm/{user.id}/{token}/{new_email}"
    )
    subject = "Email Activation"
    message = render_to_string(
        "accounts/change_email.html",
        {
            "user": user,
            "verification_link": verification_link,
        },
    )

    plain_message = strip_tags(message)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email="u-saved-test@ukr.net",
        recipient_list=[
            new_email,
        ],
        html_message=message,
    )
