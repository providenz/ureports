from django import forms


class DataTablePhotoFilterForm(forms.Form):
    settlement = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-control filter_input"}),
        required=False,
    )
    oblast = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-control filter_input"}),
        required=False,
    )
    projects = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-control filter_input"}),
        required=False,
    )
    date_from = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control filter_input"}
        ),
        required=False,
    )
    date_to = forms.DateField(
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control filter_input"}
        ),
        required=False,
    )

    # Change __init__ for accepting additional keyword argument, which used to dynamically set the choices for the city field
    def __init__(self, *args, **kwargs):
        settlements = kwargs.pop("settlements", [])
        oblasts = kwargs.pop("oblasts", [])
        projects = kwargs.pop("projects", [])
        super(DataTablePhotoFilterForm, self).__init__(*args, **kwargs)
        self.fields["settlement"].choices = settlements
        self.fields["oblast"].choices = oblasts
        self.fields["projects"].choices = projects
