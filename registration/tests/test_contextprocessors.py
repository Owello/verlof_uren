from unittest import TestCase, mock

from django.contrib.auth.models import User
from model_mommy import mommy

from registration.context_processors import default_entitlement
from registration.models import Entitlement


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
