from django.contrib.auth.models import User
from django.forms import ModelForm, DateInput, forms

from .models import LeaveRegistration


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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.years = kwargs.pop('years')
        super(LeaveRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        from_date = self.cleaned_data.get('from_date')
        end_date = self.cleaned_data.get('end_date')
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
            'username', 'first_name', 'last_name', 'email', 'is_active'
        ]
