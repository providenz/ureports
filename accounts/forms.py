from django import forms
from accounts.models import CustomUser as User
from django.forms.widgets import ClearableFileInput

from reports.models import Project


class CustomImageWidget(ClearableFileInput):
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update(
            {
                "class": "form-control form-control-sm",
            }
        )
        super().__init__(attrs=attrs)


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input-material"}), required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-material"}), required=True
    )


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "input-material"}),
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input-material"}), required=True
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "input-material"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"class": "input-material"}),
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-material"}), required=True
    )
    re_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-material"}), required=True
    )


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "input-material"}), required=True
    )


class ResetPasswordConfirmForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-material"}), required=True
    )
    re_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input-material"}), required=True
    )


class ChangeUserInfoForm(forms.Form):
    logo = forms.ImageField(widget=CustomImageWidget, required=False)
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
        required=False,
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
        required=False,
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
        required=False,
    )
    organisation_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Organisation Name"}
        ),
        required=False,
    )


from django import forms
from .models import CustomUser


class UserManagementForm(forms.ModelForm):
    donated_projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "user_type",
            "is_active",
            "is_staff",
            "organisation_name",
            "first_name",
            "last_name",
            "logo",
            "donated_projects",
        ]

    def __init__(self, *args, **kwargs):
        super(UserManagementForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields[
                "donated_projects"
            ].initial = self.instance.donated_projects.all()

    def save(self, *args, **kwargs):
        instance = super(UserManagementForm, self).save(commit=False)
        if instance.pk:
            instance.donated_projects.set(self.cleaned_data["donated_projects"])
        instance.save()
        return instance
