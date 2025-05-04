from accounts.models import CustomUser

from django import forms

from django.core.exceptions import ValidationError

from reports.models import Project


class ProjectShareForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["donors"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["donors"].queryset = CustomUser.objects.exclude(id=user.id)


# forms.py


class ShareProjectByEmailForm(forms.Form):
    email = forms.EmailField(
        label="Email to share with",
        help_text="Enter the email of the user you want to share the project with.",
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Check if there is an active user with this email.
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
        except CustomUser.DoesNotExist:
            raise ValidationError("No active user found with this email address.")

        # Check if the user is the owner of the project.
        if self.instance and self.instance.owner.email == email:
            raise ValidationError("You cannot share a project with yourself.")

        return email
