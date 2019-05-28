import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

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



