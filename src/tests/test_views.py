# This Test is to test the VIEWS to the pages work
#-------------------------------------------------------------------------------

from django.test import TestCase, Client
from django.urls import reverse
from session.models import Student

class TestViews(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register_view')
        self.login_url = reverse('login_view')
    
    def test_register_POST(self): 
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'password1': 'firsttimewelinkiwasaplayer',
            'password2': 'firsttimewelinkiwasaplayer',
            'email': 'posttest@gmail.com',
            'agreement': True
        })
        self.assertEqual(response.status_code, 302)  #assuming a redirect 
        self.assertTrue(Student.objects.filter(username='testuser').exists())

    def test_login_POST(self): 
        # First, create a user to log in
        Student.objects.create_user(username='testuser', password='password123', email='test@example.com')
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Assuming a redirect on successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated) # Assuming User is successfully logged in