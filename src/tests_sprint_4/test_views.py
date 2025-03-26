from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from courses.views import generate_permutation_view

from django.contrib.auth.models import User
from courses.models import SavedSchedule, SavedCourse

from django.contrib.auth import get_user_model
from courses.views import view_sched_view, view_saved_sched_view

from courses.views import add_course_to_sched_view, redraw_course_to_sched
from unittest.mock import patch

from django.contrib.messages.middleware import MessageMiddleware

User = get_user_model()

class AddCourseToSchedViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='TestingLebronJames', password='LebronJames123', email='LukaTroncic@gmail.com')
        self.saved_schedule = SavedSchedule.objects.create(student_id=self.user.id, sched_id=1, schedule_name="Test Schedule")
        self.saved_course = SavedCourse.objects.create(
            student_id=self.user.id,
            course_code="CS 192",
            course_details={
                'course_code': 'CS 192',
                'section_name': {'lec': 'TDE1', 'lab': 'TDE1/HUV1'},
                'units': 3.0,
                'timeslots': {'lec': (180, 1020), 'lab': (180, 360)},
                'class_days': {'lec': 'T', 'lab': 'H'},
                'offering_unit': 'DCS',
                'instructor_name': {'lec': 'FIGUEROA, LIGAYA LEAH', 'lab': 'FIGUEROA, LIGAYA LEAH'},
                'venue': {'lec': 'AECH-CLR1', 'lab': 'AECH-CLR1'},
                'capacity': 25,
                'demand': 0,
                'location': {'lec': 'UP Alumni Engineers Centennial Hall', 'lab': 'UP Alumni Engineers Centennial Hall'}
            }
        )
    
    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
    def test_add_course_to_schedule_success(self):
        request = self.factory.post(
            reverse('add_course_to_sched_view', kwargs={'sched_id': self.saved_schedule.sched_id}),
            {'course_data': str(self.saved_course.course_details)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        response = add_course_to_sched_view(request, sched_id=self.saved_schedule.sched_id)

        self.assertEqual(response.status_code, 302)  # Redirect to view_saved_sched_view
        self.assertTrue(SavedCourse.objects.filter(course_code="CS 192").exists())

    def test_add_course_to_schedule_conflict(self):
        conflicting_course = {
            'course_code': 'CS 10',
            'section_name': {'lec': 'THU'},
            'units': 3.0,
            'timeslots': {'lec': [180, 270]},  # Conflicts with CS 192
            'class_days': {'lec': 'TH'},
            'offering_unit': 'DCS',
            'instructor_name': {'lec': 'FERIA, ROMMEL'},
            'venue': {'lec': 'AECH-Seminar Room'},
            'capacity': 20,
            'demand': 0,
            'location': {'lec': 'UP Alumni Engineers Centennial Hall'}
        }

        request = self.factory.post(
            reverse('add_course_to_sched_view', kwargs={'sched_id': self.saved_schedule.sched_id}),
            {'course_data': str(conflicting_course)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        with patch('courses.views.has_conflict', return_value=True):
            response = add_course_to_sched_view(request, sched_id=self.saved_schedule.sched_id)

        self.assertEqual(response.status_code, 302)  
        self.assertTrue(SavedCourse.objects.filter(course_code="CS 10").exists())

    def test_add_course_to_schedule_unauthenticated_user(self):
        request = self.factory.post(
            reverse('add_course_to_sched_view', kwargs={'sched_id': self.saved_schedule.sched_id}),
            {'course_data': str(self.saved_course.course_details)}
        )
        request.user = User()  # Unauthenticated user
        self.add_session_to_request(request)

        response = add_course_to_sched_view(request, sched_id=self.saved_schedule.sched_id)

        #dapat may error talaga cuz unauthenticated user cannoot access this view

    def test_add_course_to_schedule_no_conflict(self):
        non_conflicting_course = {
            'course_code': 'CS 194',
            'section_name': {'lec': 'MK'},
            'units': 1.0,
            'timeslots': {'lec': (600, 660)},  # No conflict with CS 192
            'class_days': {'lec': 'M'},
            'offering_unit': 'DCS',
            'instructor_name': {'lec': 'VILLAR, JOHN JUSTINE'},
            'venue': {'lec': 'AECH-Accenture Rm'},
            'capacity': 95,
            'demand': 0,
            'location': {'lec': 'UP Alumni Engineers Centennial Hall'}
        }

        request = self.factory.post(
            reverse('add_course_to_sched_view', kwargs={'sched_id': self.saved_schedule.sched_id}),
            {'course_data': str(non_conflicting_course)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        with patch('courses.views.has_conflict', return_value=False):
            response = add_course_to_sched_view(request, sched_id=self.saved_schedule.sched_id)

        self.assertEqual(response.status_code, 302)  # Redirect to view_saved_sched_view
        self.assertTrue(SavedCourse.objects.filter(course_code="CS 194").exists()) 


        print("Classes after adding: ", )
   
    def test_remove_class_from_saved_schedule(self):
    # Simulate a POST request to remove a class from the saved schedule
        request = self.factory.post(
            reverse('view_saved_sched_view', kwargs={'sched_id': self.saved_schedule.sched_id}),
            {'class_to_remove': str(self.saved_course.course_details)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        # Add MessageMiddleware to the request
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        response = view_saved_sched_view(request, sched_id=self.saved_schedule.sched_id)

        # Verify the response redirects to the same view after removal
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SavedCourse.objects.filter(course_code="CS 194").exists())  # Ensure the course is removed
        


class RedrawCourseToSchedViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='TestingLebronJames', password='LebronJames123', email='LukaTroncic@gmail.com')
        self.saved_schedule = SavedSchedule.objects.create(student_id=self.user.id, sched_id=1, schedule_name="Test Schedule")
        self.saved_course_1 = SavedCourse.objects.create(
            student_id=self.user.id,
            course_code="CS 192",
            course_details={
                'course_code': 'CS 192',
                'section_name': {'lec': 'TDE1', 'lab': 'TDE1/HUV1'},
                'units': 3.0,
                'timeslots': {'lec': (180, 1020), 'lab': (180, 360)},
                'class_days': {'lec': 'T', 'lab': 'H'},
                'offering_unit': 'DCS',
                'instructor_name': {'lec': 'FIGUEROA, LIGAYA LEAH', 'lab': 'FIGUEROA, LIGAYA LEAH'},
                'venue': {'lec': 'AECH-CLR1', 'lab': 'AECH-CLR1'},
                'capacity': 25,
                'demand': 0,
                'location': {'lec': 'UP Alumni Engineers Centennial Hall', 'lab': 'UP Alumni Engineers Centennial Hall'}
            }
        )
        self.saved_course_2 = SavedCourse.objects.create(
            student_id=self.user.id,
            course_code='CS 194',
            course_details={
                'course_code': 'CS 194',
                'section_name': {'lec': 'MK'},
                'units': 1.0,
                'timeslots': {'lec': (600, 660)},
                'class_days': {'lec': 'M'},
                'offering_unit': 'DCS',
                'instructor_name': {'lec': 'VILLAR, JOHN JUSTINE'},
                'venue': {'lec': 'AECH-Accenture Rm'},
                'capacity': 95,
                'demand': 0,
                'location': {'seminar': 'UP Alumni Engineers Centennial Hall'}
            }
        )
            
        self.saved_schedule.courses.add(self.saved_course_1, self.saved_course_2)

    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_redraw_course_success(self):
        # Simulate a POST request to redraw a course
        new_course_data = {
            'course_code': 'CS 192',
            'section_name': {'lec': 'TBC1', 'lab': 'TBC1/HQR1'},
            'units': 3.0,
            'timeslots': {'lab': [0, 180], 'lec': [60, 180]},
            'class_days': {'lab': 'H', 'lec': 'T'},
            'offering_unit': 'DCS',
            'instructor_name': {'lab': 'FIGUEROA, LIGAYA LEAH', 'lec': 'FIGUEROA, LIGAYA LEAH'},
            'venue': {'lab': 'AECH-CLR1', 'lec': 'AECH-CLR1'},
            'capacity': 25,
            'demand': 0,
            'location': {'lab': 'UP Alumni Engineers Centennial Hall', 'lec': 'UP Alumni Engineers Centennial Hall'}
        }

        request = self.factory.post(
            reverse('redraw_course_to_sched', kwargs={'sched_id': self.saved_schedule.sched_id, 'course_code': 'CS 192'}),
            {'course_data': str(new_course_data)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        with patch('courses.views.get_all_sections', return_value=[new_course_data]):
            response = redraw_course_to_sched(request, sched_id=self.saved_schedule.sched_id, course_code='CS 192')

        self.assertEqual(response.status_code, 302)  # Redirect to view_saved_sched_view
        self.assertTrue(SavedCourse.objects.filter(course_code="CS 192", course_details__section_name={'lec': 'TBC1', 'lab': 'TBC1/HQR1'}).exists())  # Ensure the new course is added
        self.assertFalse(SavedCourse.objects.filter(course_code="CS 192", course_details__section_name={'lec': 'TDE1', 'lab': 'TDE1/HUV1'}).exists())
    def test_redraw_course_not_found(self):
        # Simulate a POST request to redraw a non-existent course
        request = self.factory.post(
            reverse('redraw_course_to_sched', kwargs={'sched_id': self.saved_schedule.sched_id, 'course_code': 'CS 999'}),
            {}
        )
        request.user = self.user
        self.add_session_to_request(request)

        # Add MessageMiddleware to the request
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        response = redraw_course_to_sched(request, sched_id=self.saved_schedule.sched_id, course_code='CS 999')

        self.assertEqual(response.status_code, 302)  # Redirect to view_saved_sched_view
    
    def test_redraw_course_conflicting_sections(self):
        # Simulate a POST request to redraw a course with conflicting sections
        conflicting_course_data = {
            'course_code': 'CS 192',
            'section_name': {'lec': 'TBC1', 'lab': 'TBC1/HQR1'},
            'units': 3.0,
            'timeslots': {'lab': [0, 180], 'lec': [60, 180]},  # Conflicts with existing course
            'class_days': {'lab': 'H', 'lec': 'T'},
            'offering_unit': 'DCS',
            'instructor_name': {'lab': 'FIGUEROA, LIGAYA LEAH', 'lec': 'FIGUEROA, LIGAYA LEAH'},
            'venue': {'lab': 'AECH-CLR1', 'lec': 'AECH-CLR1'},
            'capacity': 25,
            'demand': 0,
            'location': {'lab': 'UP Alumni Engineers Centennial Hall', 'lec': 'UP Alumni Engineers Centennial Hall'}
        }

        request = self.factory.post(
            reverse('redraw_course_to_sched', kwargs={'sched_id': self.saved_schedule.sched_id, 'course_code': 'CS 192'}),
            {'course_data': str(conflicting_course_data)}
        )
        request.user = self.user
        self.add_session_to_request(request)

        with patch('courses.views.get_all_sections', return_value=[conflicting_course_data]):
            response = redraw_course_to_sched(request, sched_id=self.saved_schedule.sched_id, course_code='CS 192')

        self.assertEqual(response.status_code, 302)  
        
    def test_view_nonexistent_schedule(self):
        # Simulate a GET request to view a schedule that does not exist
        request = self.factory.get(reverse('view_sched_view', kwargs={'sched_id': 999}))
        request.user = self.user
        self.add_session_to_request(request)

        response = view_sched_view(request, sched_id=999)
        self.assertIsNone(response)
        self.assertEqual(response.status_code, 404)  
        ## dapat mag error ren to

