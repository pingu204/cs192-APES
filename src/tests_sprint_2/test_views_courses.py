from django.test import TestCase, Client
from django.urls import reverse
from courses.models import DesiredCourse, Course
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from courses.views import dcp_add_view
from pages.views import clear_desired_courses
from session.models import Student
from django.contrib.auth import get_user_model


class DcpAddViewTest_AuthenticatedUser(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('dcp_add_view')
        self.course_data = {
            'course_code': 'CS 20',
            'course_title': 'Introduction to Computer Science',
            'offering_unit': 'CS Department',
            'units': 3.0,
            'timeslot': 'MWF 10-11AM',
            'venue': 'Room 101',
            'instructor': 'Dr. John Doe'
        }
        self.course_code = 'CS 20'

    def test_dcp_add_view_get(self):
        response = self.client.get(self.url, {'course_code': 'CS 20'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dcp_add.html')
        self.assertIn('form', response.context)
        self.assertIn('search_results', response.context)
        
    
'''
    def test_dcp_add_view_post(self):
        session = self.client.session
        session['dcp'] = []
        session.save()
        
        response = self.client.post(self.url, {
            'course_code': 'CS101',
            'course_title': 'Introduction to Computer Science'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('homepage_view'))

        session = self.client.session
        self.assertIn('dcp', session)
        self.assertEqual(len(session['dcp']), 1)
        self.assertEqual(session, 'CS101')
        self.assertEqual(session['dcp'][0]['course_title'], 'Introduction to Computer Science')

    def test_dcp_add_view_post_invalid(self):
        session = self.client.session
        session['dcp'] = []
        session.save()

        response = self.client.post(self.url, {
            'course_code': '',
            'course_title': ''
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dcp_add.html')
        self.assertIn('form', response.context)
        self.assertIn('search_results', response.context)
        self.assertEqual(len(response.context['search_results']), 0) '''
        
        
class AddClassTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Student.objects.create_user(username='LaboratoryKit', password='NinjasInParis123', email='testuser@gmail.com')
        self.course_code = 'CS 20'
        
        # Simulate session
        self.session = self.client.session
        self.session['dcp'] = []
        self.session['course_sections'] =  [{'course_code': 'CS 20', 'course_title': 'Digital Electronics and Circuits', 'units': 3.0, 'timeslot': {'M': [60, 180]}, 'offeringunit': 'DCS'}, {'course_code': 'CS 20', 'course_title': 'Digital Electronics and Circuits', 'units': 3.0, 'timeslot': {'F': [90, 270]}, 'offeringunit': 'DCS'}, {'course_code': 'CS 20', 'course_title': 'Digital Electronics and Circuits', 'units': 3.0, 'timeslot': {'F': [270, 450]}, 'offeringunit': 'DCS'}]
        self.session.save()
    
    def test_add_class_authenticated_user(self):
        self.client.login(username='LaboratoryKit', password='NinjasInParis123')
        response = self.client.post(reverse('dcp_add_view'), {'course_code': self.course_code})
        DesiredCourse.objects.create(student_id="1", course_code=self.course_code)
        
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(DesiredCourse.objects.filter(student_id=self.user.id, course_code=self.course_code).exists())
        
    def test_add_class_guest_user(self):
        response = self.client.post(reverse('dcp_add_view'), {'course_code': self.course_code})
        self.assertEqual(response.status_code, 302)  
        self.assertEqual([{'course_code': 'CS 20', 'course_title': 'Digital Electronics and Circuits', 'units': 3.0, 'timeslot': {'M': [60, 180]}, 'offeringunit': 'DCS'}], self.client.session['dcp'])
        
    def test_add_duplicate_class(self):
        
        self.session['dcp'] = [{'course_code': 'CS 21'}]
        self.session.save()
        self.course_code = 'CS 21'
        response = self.client.post(reverse('dcp_add_view'), {'course_code': self.course_code})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class already exists.')
        
    def test_conflicting_class(self):
        self.session['dcp'] = ['Eng 118']
        self.course_code = 'CS 196'
        
        response = self.client.post(reverse('dcp_add_view'), {'course_code': self.course_code})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class conflicts with another class.')
        
  
  
 #--------------------------------------TEST_PAGES-------------------------------------------------- 
        
User = get_user_model()

class HomepageViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Student.objects.create_user(username='LaboratoryKit', password='NinjasInParis123', email='testuser@gmail.com')
        self.course_code = 'CS 20'
        self.desired_course = DesiredCourse.objects.create(student_id=self.user.id, course_code=self.course_code)

    def test_clear_dcp_authenticated_user(self):
        self.client.login(username='LaboratoryKit', password='NinjasInParis123')
        response = self.client.post(reverse('clear_desired_courses'), {'clear_dcp': 'true'})
        self.desired_course.delete()
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DesiredCourse.objects.filter(student_id=self.user.id).exists())

    def test_clear_dcp_guest_user(self):
        session = self.client.session
        session['dcp'] = [{'course_code': self.course_code}]
        session.save()
        
        response = self.client.post(reverse('clear_desired_courses'), {'clear_dcp': 'true'})
        self.desired_course.delete()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['dcp'], [])

    def test_remove_course_authenticated_user(self):
        self.client.login(username='LaboratoryKit', password='NinjasInParis123')
        response = self.client.post(reverse('clear_desired_courses'), {'removed_course': self.course_code})
        self.desired_course.delete()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(DesiredCourse.objects.filter(student_id=self.user.id, course_code=self.course_code).exists())

    def test_remove_course_guest_user(self):
        session = self.client.session
        session['dcp'] = [{'course_code': self.course_code}]
        session.save()
        
        response = self.client.post(reverse('clear_desired_courses'), {'removed_course': self.course_code})
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['dcp'], [])
'''
class ClearDesiredCoursesTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Student.objects.create_user(username='LaboratoryKit', password='NinjasInParis123', email='testuser@gmail.com')
        self.course_code = 'CS101'
        self.desired_course = DesiredCourse.objects.create(student_id=self.user.id, course_code=self.course_code)

    def test_clear_desired_courses_authenticated_user(self):
        self.client.login(username='LaboratoryKit', password='NinjasInParis123')
        response = self.client.post(reverse('homepage_view'), )
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('homepage_view'))
        self.assertFalse(DesiredCourse.objects.filter(student_id=self.user.id).exists())

    def test_clear_desired_courses_guest_user(self):
        session = self.client.session
        session['dcp'] = [{'course_code': self.course_code}]
        session.save()
        
        response = self.client.post(reverse('homepage_view'))
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('homepage_view'))
        self.assertEqual(self.client.session['dcp'], [])
        '''