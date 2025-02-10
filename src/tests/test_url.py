# This Test is to test the URL/Link to the pages work
#-------------------------------------------------------------------------------
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from apes.urls import homepage_view, landing_view, register_view, successful_account_creation_view, login_view

class TestUrls(SimpleTestCase):
    def test_homepage_url_is_resolved(self):
        url = reverse('homepage_view')
        self.assertEqual(resolve(url).func, homepage_view)

    def test_landing_url_is_resolved(self):
        url = reverse('landing_view')
        self.assertEqual(resolve(url).func, landing_view)
        
    def test_register_url_is_resolved(self):
        url = reverse('register_view')
        self.assertEqual(resolve(url).func, register_view)
        
    def test_successful_account_cretion_url_is_resolved(self):
        url = reverse('successful_account_creation')
        self.assertEqual(resolve(url).func, successful_account_creation_view)
        
    def test_login_url_is_resolved(self):
        url = reverse('login_view')
        self.assertEqual(resolve(url).func, login_view)