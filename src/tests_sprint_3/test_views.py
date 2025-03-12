from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from courses.views import generate_permutation_view

class GeneratePermutationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.dcp_sections = [
            [
                {
                    'course_code': 'CS 192',
                    'course_title': 'Software Engineering II',
                    'section_name': {'lec': 'TBC1', 'lab': 'TBC1/HQR1'},
                    'units': 3.0,
                    'timeslots': {'H': [0, 180], 'T': [60, 180]},
                    'class_days': {'lab': 'H', 'lec': 'T'},
                    'offering_unit': 'DCS',
                    'instructor_name': {'lab': 'FIGUEROA, LIGAYA LEAH', 'lec': 'FIGUEROA, LIGAYA LEAH'},
                    'venue': {'lab': 'AECH-CLR1', 'lec': 'AECH-CLR1'},
                    'capacity': 25,
                    'demand': 0,
                    'location': {'lab': 'UP Alumni Engineers Centennial Hall', 'lec': 'UP Alumni Engineers Centennial Hall'}
                },
                {
                    'course_code': 'CS 192',
                    'course_title': 'Software Engineering II',
                    'section_name': {'lec': 'TBC2', 'lab': 'TBC2/HQR2'},
                    'units': 3.0,
                    'timeslots': {'H': [0, 180], 'T': [60, 180]},
                    'class_days': {'lab': 'H', 'lec': 'T'},
                    'offering_unit': 'DCS',
                    'instructor_name': {'lab': 'SOLAMO, MA. ROWENA', 'lec': 'SOLAMO, MA. ROWENA'},
                    'venue': {'lab': 'AECH-CLR2', 'lec': 'AECH-CLR2'},
                    'capacity': 33,
                    'demand': 0,
                    'location': {'lab': 'UP Alumni Engineers Centennial Hall', 'lec': 'UP Alumni Engineers Centennial Hall'}
                }
            ],
            [
                {
                    'course_code': 'CS 194',
                    'course_title': 'Undergraduate Research Seminar',
                    'section_name': {'lec': 'MK'},
                    'units': 1.0,
                    'timeslots': {'M': [600, 660]},
                    'class_days': {'lec': 'M'},
                    'offering_unit': 'DCS',
                    'instructor_name': {'lec': 'VILLAR, JOHN JUSTINE'},
                    'venue': {'seminar': 'AECH-Accenture Rm'},
                    'capacity': 95,
                    'demand': 0,
                    'location': {'seminar': 'UP Alumni Engineers Centennial Hall'}
                }
            ]
        ]

    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_generate_permutation_view(self):
        request = self.factory.get(reverse('homepage_view'))
        self.add_session_to_request(request)
        request.session['dcp_sections'] = self.dcp_sections

        response = generate_permutation_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('homepage_view'))