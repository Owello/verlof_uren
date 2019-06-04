import datetime
from unittest import TestCase

from django.core.exceptions import ValidationError

from registration.forms import LeaveRegistrationForm, EntitlementForm


class LeaveRegistrationFormTest(TestCase):
    def test_leave_registration_form_clean_data_ok(self):
        today = datetime.date.today()
        cleaned_data = {"from_date": today, "end_date": today}
        form = LeaveRegistrationForm(years=[today.year])
        form.cleaned_data = cleaned_data
        self.assertIs(form.clean(), cleaned_data)

    def test_leave_registration_form_clean_from_date_before_end_date(self):
        today = datetime.date.today()
        cleaned_data = {"from_date": today, "end_date": today - datetime.timedelta(days=1)}
        form = LeaveRegistrationForm(years=[today.year])
        form.cleaned_data = cleaned_data
        self.assertRaisesMessage(ValidationError, "De einddatum ligt voor de begindatum", form.clean)

    def test_leave_registration_form_clean_2_different_years(self):
        today = datetime.date.today()
        cleaned_data = {"from_date": today, "end_date": today - datetime.timedelta(days=365)}
        form = LeaveRegistrationForm(years=[today.year])
        form.cleaned_data = cleaned_data
        self.assertRaisesMessage(ValidationError,
                                 "Je kan voor 1 kalenderjaar tegelijk invullen. Zorg dat begin- en einddatum in het zelfde jaar liggen.",
                                 form.clean)

    def test_leave_registration_form_clean_no_years(self):
        today = datetime.date.today()
        cleaned_data = {"from_date": today, "end_date": today}
        form = LeaveRegistrationForm(years=[])
        form.cleaned_data = cleaned_data
        self.assertRaisesMessage(ValidationError, "Dit jaar is (nog) niet beschikbaar", form.clean)



"""test more clean without from_date and end_date"""

class EntitlementFormTest(TestCase):
    def test_entitlement_form_clean_data_ok(self):
        cleaned_data = {"year": 2019}
        form = EntitlementForm(years=[2018, 2017, 2016])
        form.cleaned_data = cleaned_data
        self.assertIs(form.clean(), cleaned_data)

    def test_entitlement_form_clean_existing_year(self):
        cleaned_data = {"year": 2019}
        form = EntitlementForm(years=[2019, 2018, 2017, 2016])
        form.cleaned_data = cleaned_data
        self.assertRaisesMessage(ValidationError, "Er zijn al verlofuren voor dit jaar ingevuld.", form.clean)
