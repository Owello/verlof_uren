from django.forms import ModelForm, DateInput

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
