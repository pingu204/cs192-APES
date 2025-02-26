from django.test import TestCase, Client
from django.urls import reverse
from courses.models import DesiredCourse, Course
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from courses.views import dcp_add_view

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
        self.assertEqual(session['dcp'][0]['course_code'], 'CS101')
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
        self.assertEqual(len(response.context['search_results']), 0)