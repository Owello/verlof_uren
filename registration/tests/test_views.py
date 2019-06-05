import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy

from registration.models import Entitlement, LeaveRegistration
from registration.views import Index, LeaveRegistrationCreate, LeaveRegistrationUpdate


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
        with mock.patch.object(Index, 'get_context_data') as get_context_data:
            entitlement = mommy.make(Entitlement, year=2019)
            get_context_data.return_value = {'default_entitlement': entitlement}
            self.client.login(username='employer', password='employeremployer')
            response = self.client.get(reverse('index'))
            self.assertContains(response, '<a class="massive fluid ui green basic button"')
            self.assertContains(response, 'href="/entitlement/2019"')
            self.assertContains(response, 'href="/logout')
            self.assertContains(response, 'href="/password_change/')

    def test_entitlement_last_year(self):
        with mock.patch.object(Index, 'get_context_data') as get_context_data:
            entitlement = mommy.make(Entitlement, year=2018)
            get_context_data.return_value = {'default_entitlement': entitlement}
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
        entitlement3 = mommy.make(Entitlement, user=user)
        entitlement4 = mommy.make(Entitlement, user=user)
        entitlement5 = mommy.make(Entitlement, user=user)
        response = self.client.get(reverse('entitlement-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data['all_entitlements'],
                                 [repr(entitlement3), repr(entitlement4), repr(entitlement5)], ordered=False)
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
        self.assertContains(response, 'href="/leave_registration/1/update')
        self.assertContains(response, 'href="/leave_registration/1/delete')

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


class LeaveRegistrationCreateTests(TestCase):
    fixtures = ['users.json']

    def test_not_logged_in(self):
        response = self.client.get(reverse('leave-registration-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/leave_registration/create')

    def test_logged_in_no_permission(self):
        self.client.login(username='nonuser', password='nonusernonuser')
        response = self.client.get(reverse('leave-registration-create'))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_has_permission(self):
        self.client.login(username='employee', password='employeeemployee')
        response = self.client.get(reverse('leave-registration-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_has_permission_no_entitlement(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dit jaar is (nog) niet beschikbaar')
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_wrong_year(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dit jaar is (nog) niet beschikbaar")
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_end_date_before_from_date(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-02'
        yesterday = '2019-01-01'
        mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': yesterday, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "De einddatum ligt voor de begindatum")
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_2_different_years(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        yesterday = '2018-12-31'
        mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': yesterday, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Je kan voor 1 kalenderjaar tegelijk invullen. Zorg dat begin- en einddatum \
                            in het zelfde jaar liggen.")
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_wrong_format(self):
        self.client.login(username='employee', password='employeeemployee')
        today = 'today'
        mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None,
                             "Vul een geldige datum in.")
        self.assertTemplateUsed(response, 'registration/leaveregistration_create.html')

    def test_logged_in_all_correct_2019(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/entitlement/2019')

    def test_logged_in_all_correct_2018(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2018-01-01'
        mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        response = self.client.post(reverse('leave-registration-create'),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/entitlement/2018')

    def test_get_form_kwargs(self):
        user = mommy.make(User)
        mommy.make(Entitlement, year=2019, user=user)
        mommy.make(Entitlement, year=2018, user=user)
        mommy.make(Entitlement, year=2020, user=user)
        leave_registration_view = LeaveRegistrationCreate()
        leave_registration_view.request = mock.Mock()
        leave_registration_view.request.user = user
        result = leave_registration_view.get_form_kwargs()
        self.assertCountEqual(result['years'], [2018, 2019, 2020])


class LeaveRegistrationUpdateTests(TestCase):
    fixtures = ['users.json']

    def test_not_logged_in(self):
        response = self.client.get(reverse('leave-registration-update', kwargs={'pk': 3}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/leave_registration/3/update')

    def test_logged_in_no_permission(self):
        self.client.login(username='nonuser', password='nonusernonuser')
        response = self.client.get(reverse('leave-registration-update', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_leave_registration_other_user(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employee')
        today = datetime.datetime.now()
        entitlement = mommy.make(Entitlement, user=user, year=2019)
        mommy.make(LeaveRegistration, pk=4, from_date=today, end_date=today, amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.get(reverse('leave-registration-update', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, 404)

    def test_logged_in_no_leave_registration(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employer')
        mommy.make(Entitlement, user=user, year=2019)
        response = self.client.get(reverse('leave-registration-update', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, 404)

    def test_logged_in_has_permission(self):
        self.client.login(username='employer', password='employeremployer')
        user = User.objects.get(username='employer')
        today = datetime.datetime.now()
        entitlement = mommy.make(Entitlement, user=user, year=2019)
        mommy.make(LeaveRegistration, pk=4, from_date=today, end_date=today, amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.get(reverse('leave-registration-update', kwargs={'pk': 4}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/leaveregistration_update.html')

    def test_get_form_kwargs(self):
        user = mommy.make(User)
        mommy.make(Entitlement, year=2019, user=user)
        mommy.make(Entitlement, year=2018, user=user)
        leave_registration_view = LeaveRegistrationUpdate()
        leave_registration_view.request = mock.Mock()
        leave_registration_view.request.user = user
        result = leave_registration_view.get_form_kwargs()
        self.assertCountEqual(result['years'], [2018, 2019])

    def test_has_permission_no_entitlement(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 404)

    def test_wrong_year(self):
        self.client.login(username='employee', password='employeeemployee')
        new_date = '2018-01-01'
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date=new_date, end_date=new_date, amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': new_date, 'end_date': new_date, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, "Dit jaar is (nog) niet beschikbaar")
        self.assertTemplateUsed(response, 'registration/leaveregistration_update.html')

    def test_logged_in_end_date_before_from_date(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-02'
        yesterday = '2019-01-01'
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date=today, end_date=today, amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': today, 'end_date': yesterday, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "De einddatum ligt voor de begindatum")
        self.assertTemplateUsed(response, 'registration/leaveregistration_update.html')

    def test_logged_in_2_different_years(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        yesterday = '2018-12-31'
        mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date=today, end_date=today, amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': yesterday, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Je kan voor 1 kalenderjaar tegelijk invullen. Zorg dat begin- en einddatum \
                            in het zelfde jaar liggen.")
        self.assertTemplateUsed(response, 'registration/leaveregistration_update.html')

    def test_logged_in_wrong_format(self):
        self.client.login(username='employee', password='employeeemployee')
        today = 'today'
        entitlement = mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date='2019-01-01', end_date='2019-01-01', amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None,
                             "Vul een geldige datum in.")
        self.assertTemplateUsed(response, 'registration/leaveregistration_update.html')

    def test_logged_in_all_correct_2019(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2019-01-01'
        entitlement = mommy.make(Entitlement, year=2019, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date='2019-01-01', end_date='2019-01-01', amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/entitlement/2019')

    def test_logged_in_all_correct_2018(self):
        self.client.login(username='employee', password='employeeemployee')
        today = '2018-01-01'
        entitlement = mommy.make(Entitlement, year=2018, user=User.objects.get(username='employee'))
        mommy.make(LeaveRegistration, pk=4, from_date='2018-01-01', end_date='2018-01-01', amount_of_hours=8,
                   entitlement=entitlement)
        response = self.client.post(reverse('leave-registration-update', kwargs={'pk': 4}),
                                    {'from_date': today, 'end_date': today, 'amount_of_hours': '8'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/entitlement/2018')
