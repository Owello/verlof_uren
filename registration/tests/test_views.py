from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_view_url_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)

    # def test_view_uses_correct_template(self):
    #     response = self.client.get(reverse('index'))
    #     self.assertEquals(response.status_code, 302)
    #     self.assertTemplateUsed(response, 'login.html')

    # def test_home_page_contains_correct_html(self):
    #     response = self.client.get('/')
    #     self.assertContains(response, '<h1>Homepage</h1>')
    #
    # def test_home_page_does_not_contain_incorrect_html(self):
    #     response = self.client.get('/')
    #     self.assertNotContains(
    #         response, 'Hi there! I should not be on the page.')
