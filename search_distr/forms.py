from django import forms
import datetime

from search_distr.models import Person, Region, Settlement
from reports.models import Category


class PersonForm(forms.ModelForm):
        class Meta:
            model = Person
            fields = [
                "name",
                "address",
                "phone",
                "age",
                "gender",
                "is_idp",
                "is_pwd",
                "is_returnees",
            ]


class XLSXUploadForm(forms.Form):
    xlsx_file = forms.FileField(
        label=" Upload XLSX File",
        widget=forms.ClearableFileInput(),
    )


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = [
            "name",
        ]


class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ["name", "community", "district"]


class MonthComparison(forms.Form):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    YEAR_CHOICES = [(year, year) for year in range(datetime.datetime.now().year, 1900, -1)]

    m1 = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    m2 = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    y1 = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    y2 = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    # category_choices = Category.objects.values_list('id', 'name')
    category_choices = []
    category = forms.ChoiceField(choices=category_choices, widget=forms.Select(attrs={'class': 'form-control'}), required=True)


# from django import forms
# import datetime

# from search_distr.models import Person, Region, Settlement
# from reports.models import Category


# class PersonForm(forms.ModelForm):
#     pass


# class XLSXUploadForm(forms.Form):
#     pass


# class RegionForm(forms.ModelForm):
#     pass

# class SettlementForm(forms.ModelForm):
#     pass


# class MonthComparison(forms.Form):
#     pass
