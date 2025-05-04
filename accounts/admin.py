from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    # Опционально, вы можете переопределить поля, отображаемые в админ-панели
    fieldsets = (
        (None, {"fields": ("email", "password", "user_type", "manager_access", "logo", "username")}),
        ("Personal info", {"fields": ("first_name", "last_name", "organisation_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "user_type", "logo"),
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "is_staff", "user_type")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
