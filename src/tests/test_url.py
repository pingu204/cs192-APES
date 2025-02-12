# This Test is to test the URL/Link to the pages work
#-------------------------------------------------------------------------------
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from apes.urls import homepage_view, landing_view, register_view, successful_account_creation_view, login_view, logout_view, guest_login_view


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
        
    def test_successful_account_creation_url_is_resolved(self):
        url = reverse('successful_account_creation')
        self.assertEqual(resolve(url).func, successful_account_creation_view)
        
    def test_login_url_is_resolved(self):
        url = reverse('login_view')
        self.assertEqual(resolve(url).func, login_view)
        
    def test_guest_url_is_resolved(self):
        url = reverse('guest_login_view')
        self.assertEqual(resolve(url).func, guest_login_view)
        
    def test_logout_url_is_resolved(self):
        url = reverse('logout_view')
        self.assertEqual(resolve(url).func, logout_view)
        
        
        

    def test_invalid_url(self):
        url = '/invalid-url/'
        with self.assertRaises(Exception):
            resolve(url)

    def test_empty_url(self):
        url = ''
        with self.assertRaises(Exception):
            resolve(url)

    def test_url_with_invalid_characters(self):
        url = '/invalid-url-@#$/'
        with self.assertRaises(Exception):
            resolve(url)

    def test_homepage_url_with_extra_parameters(self): 
        url = reverse('homepage_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, homepage_view)

    def test_landing_url_with_extra_parameters(self):
        url = reverse('landing_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, landing_view)

    def test_register_url_with_extra_parameters(self):
        url = reverse('register_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, register_view)

    def test_successful_account_creation_url_with_extra_parameters(self):
        url = reverse('successful_account_creation') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, successful_account_creation_view)

    def test_login_url_with_extra_parameters(self):
        url = reverse('login_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, login_view)
        
    def test_guest_url_with_extra_parameters(self):
        url = reverse('guest_login_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, guest_login_view)
        
    def test_logout_url_with_extra_parameters(self):
        url = reverse('logout_view') + '?param=value'
        self.assertEqual(resolve(url.split('?')[0]).func, logout_view)
        