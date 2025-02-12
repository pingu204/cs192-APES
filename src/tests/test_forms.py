# This Test is to test the VIEWS to the pages work
#-------------------------------------------------------------------------------

from django.test import TestCase
from session.forms import UserRegisterForm, UserAuthenticationForm
from session.models import Student



class TestForms(TestCase):
    #test whether the form is valid with complete details
    def test_user_regis_form_valid(self):
        
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': 'Djangoplease123',
            'password2': 'Djangoplease123',
            'agreement' : True
        })
        self.assertTrue(form.is_valid())
        
    #test whether the form is invalid with no details
    def test_user_regis_form_no_data(self):
        form = UserRegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 5)  
        
    #test whether the form is invalid with no username
    def test_user_regis_form_no_username(self):
        form = UserRegisterForm(data={
            'username': None,
            'email': 'test@gmail.com',
            'password1': 'Djangoplease123',
            'password2': 'Djangoplease123',
            'agreement' : True})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  
    
    #test whether the form is invalid with no email
    def test_user_regis_form_no_email(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': '',
            'password1': 'Djangoplease123',
            'password2': 'Djangoplease123',
            'agreement' : True})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  
        
    #test whether the form is invalid with no password1
    def test_user_regis_form_no_password1(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': ' ',
            'password2': 'Djangoplease123',
            'agreement': True
        })
        #self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2) 
        
        
    #test whether the form is invalid with no password2
    def test_user_regis_form_no_password2(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': 'Djangoplease123',
            'password2': '',
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  
        
    #test whether the form is invalid with no agreement
    def test_user_regis_form_no_agreement(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': 'Djangoplease123',
            'password2': 'Djangoplease123',
            'agreement': None
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  
        
    #test whether the form is invalid with password1 and password2 not matching
    def test_user_regis_form_not_matching_passwords(self):
        form = UserRegisterForm(data={
            'username': 'testuser',
            'email': 'test@gmail.com',
            'password1': 'Pythonplease123',
            'password2': 'Djangoplease123',
            'agreement': True
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  

class TestUserRegisterForm(TestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            username='existinguser',
            email='existing@gmail.com',
            password= 'Imalreadyhere123'
        )
    #testing whether unique username is enforced
    def test_user_regis_form_unique_username(self):
        form = UserRegisterForm(data={
            'username': 'existinguser',
            'email': 'newest@gmail.com',
            'password1': 'Imalreadyhere123',
            'password2': 'Imalreadyhere123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    #testing whether unique email is enforced
    def test_user_regis_form_taken_email(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'existing@gmail.com',
            'password1': 'Ithoughtiwasafastlearner123',
            'password2': 'Ithoughtiwasafastlearner123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    #testing whether weak password is enforced (less than 8 characters)
    def test_user_regis_form_weak_password_less_characters(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': '123',
            'password2': '123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        #self.assertIn('password1', form.errors)
        #self.assertIn('password2', form.errors)
        
    #testing whether weak password is enforced (need atleast 1 number)
    def test_user_regis_form_weak_password_one_number(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Allbecauseilikedaboy',
            'password2': 'Allbecauseilikedaboy',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        #self.assertIn('password1', form.errors)
        #self.assertIn('password2', form.errors)
        
    #testing whether weak password is enforced (need atleast 1 capital letter and 1 small letter)
    def test_user_regis_form_weak_password_one_capital_small(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'allbecauseilikedaboy12',
            'password2': 'allbecauseilikedaboy12',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        #self.assertIn('password1', form.errors)
        #self.assertIn('password2', form.errors)
        
    #testing whether weak password is enforced (need atleast 1 capital letter and 1 small letter)
    def test_user_regis_form_weak_password_too_common(self):
        form = UserRegisterForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Password123',
            'password2': 'Password123',
            'agreement' : True
        })
        self.assertFalse(form.is_valid())
        #self.assertIn('password1', form.errors)
        #self.assertIn('password2', form.errors)
        
        
class TestUserAuthenticationForm(TestCase):
    #setting up an account for testing
    def setUp(self):
        self.student = Student.objects.create_user(
            username= 'testinguser',
            email='authenticate@gmail.com',
            password= 'Authenticateme123'
        )
    #testing whether the form is valid with correct account details (through username)
    def test_user_auth_form_username_valid(self):
        form = UserAuthenticationForm(data={
            'username': 'testinguser',
            'password': 'Authenticateme123'
        })
        
        self.assertTrue(form.is_valid())
        
    #testing whether the form is valid with correct account details (through email)
    def test_user_auth_form_email_valid(self):
        form = UserAuthenticationForm(data={
            'username': 'authenticate@gmail.com',
            'password': 'Authenticateme123'
        })
        
        self.assertTrue(form.is_valid())

    #testing whether the form is invalid with no details
    def test_user_auth_form_no_data(self):
        form = UserAuthenticationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3) ##
        
    #testing whether the form is invalid with wrong username
    def test_user_auth_form_wrong_data_username(self):
        form = UserAuthenticationForm(data={
            'username': 'wronguser',
            'password': 'Authenticateme123'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1) ##
        
    #testing whether the form is invalid with wrong email
    def test_user_auth_form_wrong_data_email(self):
        form = UserAuthenticationForm(data={
            'username': 'wrongemail@gmail.com',
            'password': 'Authenticateme123'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1) ##
        
    #testing whether the form is invalid with wrong password
    def test_user_auth_form_wrong_data_password(self):
        form = UserAuthenticationForm(data={
            'username': 'authenticate@gmail.com',
            'password': 'Wrongpassword123'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1) ##