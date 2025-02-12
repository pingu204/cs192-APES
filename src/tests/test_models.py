# This Test is to test the Models 
#-------------------------------------------------------------------------------
from django.test import TestCase
from django.utils.text import slugify
from session.models import Student

from django.test import TestCase
from session.models import Student

class TestModels(TestCase):
    #creates a student object
    def setUp(self):
        self.student = Student.objects.create_user(
            username='testuser',
            email='test@gmail.com',
            password='Iwillfinishthis123'
        )
        
    #tests if the creation is correct
    def test_student_creation(self):
        #check for correct
        self.assertEqual(self.student.username, 'testuser')
        self.assertEqual(self.student.email, 'test@gmail.com')
        self.assertTrue(self.student.check_password('Iwillfinishthis123'))
        
        #check for wrong
        self.assertNotEqual(self.student.username, 'raaah')
        self.assertNotEqual(self.student.email, 'raaah@example.com')
        self.assertFalse(self.student.check_password('Raaahtaah123'))
        
        
       

    #tests if the creation is correct
    def test_student_str(self): 
        self.assertEqual(str(self.student.username), 'testuser')
        
        
  
        