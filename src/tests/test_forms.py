# This Test is to test the VIEWS to the pages work
#-------------------------------------------------------------------------------

from django.test import SimpleTestCase, TestCase
from session.forms import UserRegisterForm, UserAuthenticationForm
from session.models import Student
from django import forms

class TestForms(SimpleTestCase):
    def test_user_regis_form_valid(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'password123',
            'password2': 'password123',
            'agreement' : 'True'
        })
        print(form.is_valid())
        self.assertTrue(form.is_valid())

    def test_user_regis_form_no_data(self):
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  # Assuming 4 required fields: username, email, password1, password2

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

class TestUserRegisterForm(TestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='password123'
        )

    def test_user_regis_form_unique_username(self):
        form = UserRegisterForm(data={
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_regis_form_weak_password(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': '123',
            'password2': '123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_user_regis_form_taken_email(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)