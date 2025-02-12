from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.db import connection, OperationalError
from django.conf import settings

class TestDatabaseConnection(TestCase):
    def setUp(self):
        self.client = Client()

    def test_database_connection(self):
        try:
            #Try to open a connection to the database
            connection.ensure_connection()
            response = self.client.get(reverse('homepage_view'))  
            self.assertEqual(response.status_code, 302)
        except OperationalError:
            #If there is an OperationalError, it should route to /databaseerror/
            response = self.client.get(reverse('database_error_view'))  
            self.assertEqual(response.status_code, 500)
            
    
@override_settings(DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'notavalidppathtothedatabase.sqlite3',  # Invalid path to simulate database error
            }
        })

class TestDatabaseConnectionError(TestCase): #FAILED
    def setUp(self):
        self.client = Client()
    
    def test_database_connection_error(self):
        print("Current DB settings:", settings.DATABASES)

        response = self.client.post(reverse('register_view'), {
            'username': 'testuser',
            'password1': 'firsttimewelinkiwasaplayer',
            
        })
        print(response)
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, 'database_error.html')
        self.assertContains(response, "Timeout: Database connection failed.")