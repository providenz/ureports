from django import forms
from .models import Marker


class MarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ["latitude", "longitude", "comment"]
