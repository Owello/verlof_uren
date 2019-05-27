import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from model_mommy import mommy

from registration.context_processors import default_entitlement
from registration.forms import LeaveRegistrationForm, EntitlementForm
from registration.models import Entitlement, LeaveRegistration


class EntitlementQuerysetTest(TestCase):
    def test_entitlement_queryset_more_leaveregistrations(self):
        today = datetime.date.today()
        user = mommy.make(User)
        entitlement = mommy.make(Entitlement, user=user, year=today.year, leave_hours=100)
        for i in range(3):
            mommy.make(LeaveRegistration, entitlement=entitlement, from_date=today, end_date=today, amount_of_hours=8)
        entitlement_used_leave_hours = (
            (Entitlement.objects.filter(user=user).annotate_used_leave_hours()).get(user=user)).used_leave_hours
        self.assertEqual(entitlement_used_leave_hours, 24)

    def test_entitlement_queryset_1_leaveregistration(self):
        today = datetime.date.today()
        user = mommy.make(User)
        entitlement = mommy.make(Entitlement, user=user, year=today.year, leave_hours=100)
        for i in range(1):
            mommy.make(LeaveRegistration, entitlement=entitlement, from_date=today, end_date=today, amount_of_hours=8)
        entitlement_used_leave_hours = (
            (Entitlement.objects.filter(user=user).annotate_used_leave_hours()).get(user=user)).used_leave_hours
        self.assertEqual(entitlement_used_leave_hours, 8)

    def test_entitlement_queryset_0_leaveregistrations(self):
        today = datetime.date.today()
        user = mommy.make(User)
        mommy.make(Entitlement, user=user, year=today.year, leave_hours=100)
        entitlement_used_leave_hours = (
            (Entitlement.objects.filter(user=user).annotate_used_leave_hours()).get(user=user)).used_leave_hours
        self.assertEqual(entitlement_used_leave_hours, 0)

    def test_entitlement_queryset_leaveregistration_negative(self):
        today = datetime.date.today()
        user = mommy.make('User')
        entitlement = mommy.make(Entitlement, user=user, year=today.year, leave_hours=100)
        mommy.make(LeaveRegistration, entitlement=entitlement, from_date=today, end_date=today, amount_of_hours=-102)
        mommy.make(LeaveRegistration, entitlement=entitlement, from_date=today, end_date=today, amount_of_hours=-10)
        entitlement_used_leave_hours = (
            (Entitlement.objects.filter(user=user).annotate_used_leave_hours()).get(user=user)).used_leave_hours
        self.assertEqual(entitlement_used_leave_hours, -112)


class EntitlementTest(TestCase):
    def test_entitlement(self):
        leave_hours = 100
        year = datetime.date.today().year
        user = mommy.make(User)
        entitlement = mommy.make(Entitlement, user=user, year=year, leave_hours=leave_hours)
        self.assertEqual(entitlement.leave_hours, leave_hours)
        self.assertEqual(entitlement.year, datetime.datetime.now().year)

    def test_entitlement_with_negative_value(self):
        leave_hours = -100
        year = datetime.date.today().year
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=year, leave_hours=leave_hours)
        self.assertEqual(entitlement.leave_hours, leave_hours)
        self.assertEqual(entitlement.year, datetime.datetime.now().year)
        self.assertEqual(entitlement.__str__(), "<Entitlement user=test year=2019>")

    def test_entitlement_get_color_red(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_remainder_hours = mock.Mock()
        entitlement.get_remainder_hours.return_value = -15
        self.assertEqual(entitlement.get_color(), 'red')

    def test_entitlement_get_color_green(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_remainder_hours = mock.Mock()
        entitlement.get_remainder_hours.return_value = 25
        self.assertEqual(entitlement.get_color(), 'green')

    def test_entitlement_get_color_orange(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_remainder_hours = mock.Mock()
        entitlement.get_remainder_hours.return_value = 24
        self.assertEqual(entitlement.get_color(), 'orange')
        entitlement.get_remainder_hours.return_value = 0
        self.assertEqual(entitlement.get_color(), 'orange')

    def test_entitlement_get_remainder_hours_positive(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_used_hours = mock.Mock()
        entitlement.get_used_hours.return_value = 20
        self.assertEqual(entitlement.get_remainder_hours(), 80)

    def test_entitlement_get_remainder_hours_negative(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_used_hours = mock.Mock()
        entitlement.get_used_hours.return_value = 120
        self.assertEqual(entitlement.get_remainder_hours(), -20)

    def test_entitlement_get_remainder_hours_zero(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.get_used_hours = mock.Mock()
        entitlement.get_used_hours.return_value = 100
        self.assertEqual(entitlement.get_remainder_hours(), 0)

    def test_get_used_hours_no_attribute(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        with self.assertRaises(AttributeError):
            entitlement.get_used_hours()

    def test_get_used_hours_attribute(self):
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=2019, leave_hours=100)
        entitlement.used_leave_hours = 10
        self.assertEqual(entitlement.get_used_hours(), 10)


class LeaveRegistrationTest(TestCase):
    def test_leaveregistration(self):
        amount_of_hours = 8
        today = datetime.date.today()
        year = today.year
        user = mommy.make(User, username='test')
        entitlement = mommy.make(Entitlement, user=user, year=year, leave_hours=100)
        leave_registration = mommy.make(LeaveRegistration, entitlement=entitlement, from_date=today, end_date=today,
                                        amount_of_hours=8, id="1")
        self.assertEqual(leave_registration.amount_of_hours, amount_of_hours)
        self.assertEqual(leave_registration.from_date, datetime.date.today())
        self.assertEqual(leave_registration.end_date, datetime.date.today())
        self.assertEqual(leave_registration.__str__(), "1")


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


class DefaultEntitlementTest(TestCase):
    def test_default_entitlement_not_authenticated(self):
        request = mock.Mock()
        request.user = mommy.make(User)
        with mock.patch("django.contrib.auth.models.User.is_authenticated", new=False):
            result = default_entitlement(request)
            self.assertIsNone(result['default_entitlement'])

    def test_default_entitlement_no_entitlement(self):
        request = mock.Mock()
        request.user = mommy.make(User)
        result = default_entitlement(request)
        self.assertIsNone(result['default_entitlement'])

    def test_default_entitlement_is_current_year(self):
        user = mommy.make(User)
        entitlement = mommy.make(Entitlement, year=2019, user=user)
        mommy.make(Entitlement, year=2018, user=user)
        request = mock.Mock()
        request.user = user
        result = default_entitlement(request)
        self.assertEqual(result['default_entitlement'], entitlement)

    def test_default_entitlement_is_other_year(self):
        user = mommy.make(User)
        entitlement = mommy.make(Entitlement, year=2018, user=user)
        mommy.make(Entitlement, year=2017, user=user)
        request = mock.Mock()
        request.user = user
        result = default_entitlement(request)
        self.assertEqual(result['default_entitlement'], entitlement)
