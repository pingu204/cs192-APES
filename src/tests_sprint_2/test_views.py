from django.test import TestCase, Client
from django.urls import reverse
from courses.models import DesiredCourse
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from courses.views import dcp_add_view
from courses.schedule import Course

class DcpAddViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('dcp_add_view')
        self.course_data = {
            'course_code': 'CS101',
            'course_title': 'Introduction to Computer Science',
            'offering_unit': 'CS Department',
            'units': 3.0,
            'timeslot': 'MWF 10-11AM',
            'venue': 'Room 101',
            'instructor': 'Dr. John Doe'
        }

    def test_dcp_add_view_get(self):
        response = self.client.get(self.url, {'course_code': 'CS101'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dcp_add.html')
        self.assertIn('form', response.context)
        self.assertIn('search_results', response.context)


