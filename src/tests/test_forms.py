# This Test is to test the VIEWS to the pages work
#-------------------------------------------------------------------------------

from django.test import SimpleTestCase
from session.forms import UserRegisterForm, UserAuthenticationForm


class TestForms(SimpleTestCase):
    
    def test_user_regis_form_valid(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertTrue(form.is_valid())

    def test_user_regis_form_no_data(self):
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)  # Assuming 4 required fields: username, email, password1, password2

    def test_user_auth_form_valid(self):
        form = UserAuthenticationForm(data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertTrue(form.is_valid())

    def test_user_auth_form_no_data(self):
        form = UserAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Assuming 2 required fields: username, password
    
        
