from datetime import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from registration.models import Entitlement, LeaveRegistration


class HomePageTests(TestCase):
    fixtures = ['users.json']

    def test_not_logged_in(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

    def test_logged_in_no_permission(self):
        self.client.login(username='nonuser', password='nonusernonuser')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_has_permission(self):
        self.client.login(username='employer', password='employeremployer')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/home.html')

    def test_no_entitlement(self):
        with mock.patch("registration.context_processors.default_entitlement") as mock_default_entitlement:
            mock_default_entitlement.return_value = {'default_entitlement': None}
            self.client.login(username='employer', password='employeremployer')
            response = self.client.get(reverse('index'))
            self.assertContains(response,
                                '<h3 class="ui center aligned header">Er zijn nog geen gegevens beschikbaar.</h3>')

    def test_entitlement_current(self):
        with mock.patch("registration.context_processors.default_entitlement") as mock_default_entitlement:
            entitlement = mommy.make(Entitlement, year=2019)
            mock_default_entitlement.return_value = {'default_entitlement': entitlement}
            self.client.login(username='employer', password='employeremployer')
            response = self.client.get(reverse('index'))
            self.assertContains(response,
                                '<a class="massive fluid ui green basic button"')
            self.assertContains(response, 'href="/entitlement/2019"')
            self.assertContains(response, 'href="/logout')
            self.assertContains(response, 'href="/password_change/')

    def test_entitlement_last_year(self):
        with mock.patch("registration.context_processors.default_entitlement") as mock_default_entitlement:
            entitlement = mommy.make(Entitlement, year=2018)
            mock_default_entitlement.return_value = {'default_entitlement': entitlement}
            self.client.login(username='employer', password='employeremployer')
            response = self.client.get(reverse('index'))
            self.assertContains(response, '<a class="massive fluid ui green basic button"')
            self.assertContains(response, 'href="/entitlement/2018"')
            self.assertContains(response, 'href="/logout')
            self.assertContains(response, 'href="/password_change/')


class EntitlementListTests(TestCase):
    fixtures = ['users.json']

    def test_not_logged_in(self):
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/entitlement_list')

    def test_logged_in_no_permission(self):
        self.client.login(username='nonuser', password='nonusernonuser')
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 403)
        # self.assertTemplateUsed(response, 'registration/entitlement_list.html')

    def test_logged_in_has_permission(self):
        self.client.login(username='employer', password='employeremployer')
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/entitlement_list.html')

    def test_one_entitlement(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employer')
        entitlement = mommy.make(Entitlement, user=user)
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'], [repr(entitlement)])
        self.assertContains(response, '<tr>', count=2)

    def test_two_entitlement(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employer')
        entitlement1 = mommy.make(Entitlement, user=user)
        entitlement2 = mommy.make(Entitlement, user=user)
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'],
                                 [repr(entitlement1), repr(entitlement2)], ordered=False)
        self.assertContains(response, '<tr>', count=3)

    def test_three_entitlement(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employer')
        entitlement1 = mommy.make(Entitlement, user=user)
        entitlement2 = mommy.make(Entitlement, user=user)
        entitlement3 = mommy.make(Entitlement, user=user)
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'],
                                 [repr(entitlement1), repr(entitlement2), repr(entitlement3)], ordered=False)
        self.assertContains(response, '<tr>', count=4)


class EntitlementDetailTests(TestCase):
    fixtures = ['users.json']

    def test_not_logged_in(self):
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/entitlement/2019')

    def test_logged_in_no_permission(self):
        self.client.login(username='nonuser', password='nonusernonuser')
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_has_permission_no_entitlement(self):
        self.client.login(username='employer', password='employeremployer')
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 404)

    def test_with_entitlement_no_leaveregistration(self):
        self.client.login(username='employer', password='employeremployer')
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employer'))
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'], [repr(entitlement)])
        self.assertContains(response, '<tr>', count=6)

    def test_one_leaveregistration(self):
        self.client.login(username='employer', password='employeremployer')
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employer'))
        leaveregistration = mommy.make(LeaveRegistration, entitlement=entitlement)
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'], [repr(entitlement)])
        self.assertQuerysetEqual(response.context_data['all_leave_registrations'], [repr(leaveregistration)])
        self.assertContains(response, '<tr>', count=7)

    def test_two_leaveregistrations(self):
        self.client.login(username='employer', password='employeremployer')
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employer'))
        leaveregistration1 = mommy.make(LeaveRegistration, entitlement=entitlement)
        leaveregistration2 = mommy.make(LeaveRegistration, entitlement=entitlement)
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'], [repr(entitlement)])
        self.assertQuerysetEqual(response.context_data['all_leave_registrations'],
                                 [repr(leaveregistration1), repr(leaveregistration2)], ordered=False)
        self.assertContains(response, '<tr>', count=8)

    def test_three_leaveregistrations(self):
        self.client.login(username='employer', password='employeremployer')
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employer'))
        leaveregistration1 = mommy.make(LeaveRegistration, entitlement=entitlement)
        leaveregistration2 = mommy.make(LeaveRegistration, entitlement=entitlement)
        leaveregistration3 = mommy.make(LeaveRegistration, entitlement=entitlement)
        response = self.client.get(reverse('entitlement-detail', kwargs={'year': 2019}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'], [repr(entitlement)])
        self.assertQuerysetEqual(response.context_data['all_leave_registrations'],
                                 [repr(leaveregistration1), repr(leaveregistration2), repr(leaveregistration3)],
                                 ordered=False)
        self.assertContains(response, '<tr>', count=9)
