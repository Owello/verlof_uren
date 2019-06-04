import datetime

from django.contrib.auth.models import User
from django.forms import ModelForm, DateInput, forms, CheckboxSelectMultiple

from .models import LeaveRegistration, Entitlement


class LeaveRegistrationForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = LeaveRegistration
        fields = [
            'from_date', 'end_date', 'amount_of_hours'
        ]
        widgets = {
            'from_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'})
        }

    def __init__(self, years, *args, **kwargs):
        self.years = years
        super(LeaveRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        from_date = self.cleaned_data.get('from_date')
        end_date = self.cleaned_data.get('end_date')
        if not isinstance(from_date, datetime.date) or not isinstance(end_date, datetime.date):
            raise forms.ValidationError("Vul een geldige datum in")
        from_year = from_date.year
        end_year = end_date.year
        if from_year != end_year:
            raise forms.ValidationError(
                "Je kan voor 1 kalenderjaar tegelijk invullen. Zorg dat begin- en einddatum in het zelfde jaar liggen.")
        if end_date < from_date:
            raise forms.ValidationError("De einddatum ligt voor de begindatum")
        if from_year not in self.years:
            raise forms.ValidationError("Dit jaar is (nog) niet beschikbaar")
        return self.cleaned_data


class UserForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'is_active', 'groups'
        ]
        widgets = {
            'groups': CheckboxSelectMultiple()
        }


class EntitlementForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Entitlement
        fields = [
            'year', 'leave_hours'
        ]

    def __init__(self, *args, **kwargs):
        self.years = kwargs.pop('years')
        super(EntitlementForm, self).__init__(*args, **kwargs)

    def clean(self):
        year = self.cleaned_data.get('year')
        if year in self.years:
            raise forms.ValidationError(
                "Er zijn al verlofuren voor dit jaar ingevuld.")

        return self.cleaned_data


class AdminEntitlementForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Entitlement
        fields = [
            'leave_hours'
        ]
