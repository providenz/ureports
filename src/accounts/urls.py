from django.urls import path
from accounts import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    path("activate/<int:uid>/<str:token>/", views.activate, name="activate"),
    path("activate_info/", views.activate_info, name="activate_info"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path(
        "reset_password_confirm/<int:uid>/<str:token>/",
        views.reset_password_confirm,
        name="reset_password_confirm",
    ),
    path("reset_password_info/", views.reset_password_info, name="reset_password_info"),
    path(
        "reset_password_confirm_success/",
        views.reset_password_confirm_success,
        name="reset_password_confirm_success",
    ),
    path("profile/", views.profile, name="profile"),
    path("change_email/", views.change_email, name="change_email"),
    path("change_email_info/", views.change_email_info, name="change_email_info"),
    path(
        "change_email_confirm/<int:uid>/<str:token>/<str:email>",
        views.change_email_confirm,
        name="change_email_success",
    ),
    path("delete/", views.delete_account, name="delete_account"),
    path("manage-users/", views.manage_users, name="manage_users"),
    path("edit-user/<int:user_id>/", views.edit_user, name="edit_user"),
    path("delete-user/<int:user_id>/", views.delete_user, name="delete_user"),
]
