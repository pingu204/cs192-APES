from django.test import TestCase, RequestFactory, override_settings
from django.db.utils import OperationalError
from django.http import HttpResponse
from apes.middleware import DatabaseErrorMiddleware
from django.db import connections

class DatabaseSucceed(TestCase):
    
    def test_successful_database_connection(self):
        """Test if the database connection is successful."""
        db_conn = connections['default']
        try:
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")  # Execute a simple query
            self.assertTrue(True)  # Test passes if no exception occurs
        except OperationalError:
            self.fail("Database connection failed when it should have succeeded.")

class DatabaseErrorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = DatabaseErrorMiddleware(get_response=lambda request: None)
    
    @override_settings( DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nocorrectdatabasedb.sqlite3', 
    }})
    
    
    def test_database_error_handling(self):
        request = self.factory.get('/some-url/')
        
        # Simulate a database error
        exception = OperationalError("Simulated database connection error")
        
        response = self.middleware.process_exception(request, exception)
        
        # Check if the middleware returns the correct response
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Timeout: Database connection failed", response.content.decode())
        
    