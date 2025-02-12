# This Test is to test the VIEWS to the pages work
#-------------------------------------------------------------------------------

from django.test import SimpleTestCase, TestCase
from session.forms import UserRegisterForm, UserAuthenticationForm
from session.models import Student



class TestForms(TestCase):
    
    
    def test_user_regis_form_valid(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': 'djangoplease123',
            'password2': 'djangoplease123',
            'agreement' : True
        })
        
        
        self.assertTrue(form.is_valid())

    def test_user_regis_form_no_data(self):
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  

    def test_user_auth_form_valid(self):
        form = UserAuthenticationForm(data={
            'username_or_email': 'testinguser',
            'password': 'authenticateme123'
        })
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_user_auth_form_no_data(self):
        form = UserAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)  # Assuming 2 required fields: username, password

class TestUserRegisterForm(TestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            username='existinguser',
            email='existing@gmail.com',
            password= 'imalreadyhere123'
        )
    #testing whether unique username is enforced
    def test_user_regis_form_unique_username(self):
        form = UserRegisterForm(data={
            'username': 'existinguser',
            'email': 'newest@gmail.com',
            'password1': 'imalreadyhere123',
            'password2': 'imalreadyhere123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    #testing whether weak password is enforced
    def test_user_regis_form_weak_password(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': '123',
            'password2': '123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    #testing whether unique email is enforced
    def test_user_regis_form_taken_email(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'existing@gmail.com',
            'password1': 'ithoughtiwasafastlearner123',
            'password2': 'ithoughtiwasafastlearner123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)