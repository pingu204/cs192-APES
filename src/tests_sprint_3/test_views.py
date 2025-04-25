from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from courses.views import generate_permutation_view
from django.contrib.auth.models import User
from courses.models import SavedSchedule, SavedCourse

from django.contrib.auth import get_user_model

User = get_user_model()


class GeneratePermutationViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="TestingLebronJames",
            password="LebronJames123",
            email="LukaTroncic@gmail.com",
        )
        self.dcp_sections = [
            [
                {
                    "course_code": "CS 192",
                    "course_title": "Software Engineering II",
                    "section_name": {"lec": "TBC1", "lab": "TBC1/HQR1"},
                    "units": 3.0,
                    "timeslots": {"H": [0, 180], "T": [60, 180]},
                    "class_days": {"lab": "H", "lec": "T"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lab": "FIGUEROA, LIGAYA LEAH",
                        "lec": "FIGUEROA, LIGAYA LEAH",
                    },
                    "venue": {"lab": "AECH-CLR1", "lec": "AECH-CLR1"},
                    "capacity": 25,
                    "demand": 0,
                    "location": {
                        "lab": "UP Alumni Engineers Centennial Hall",
                        "lec": "UP Alumni Engineers Centennial Hall",
                    },
                },
                {
                    "course_code": "CS 192",
                    "course_title": "Software Engineering II",
                    "section_name": {"lec": "TBC2", "lab": "TBC2/HQR2"},
                    "units": 3.0,
                    "timeslots": {"H": [0, 180], "T": [60, 180]},
                    "class_days": {"lab": "H", "lec": "T"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lab": "SOLAMO, MA. ROWENA",
                        "lec": "SOLAMO, MA. ROWENA",
                    },
                    "venue": {"lab": "AECH-CLR2", "lec": "AECH-CLR2"},
                    "capacity": 33,
                    "demand": 0,
                    "location": {
                        "lab": "UP Alumni Engineers Centennial Hall",
                        "lec": "UP Alumni Engineers Centennial Hall",
                    },
                },
                {
                    "course_code": "CS 192",
                    "course_title": "Software Engineering II",
                    "section_name": {"lec": "TDE1", "lab": "TDE1/HUV1"},
                    "units": 3.0,
                    "timeslots": {"T": [180, 1020], "H": [180, 360]},
                    "class_days": {"lec": "T", "lab": "H"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lec": "FIGUEROA, LIGAYA LEAH",
                        "lab": "FIGUEROA, LIGAYA LEAH",
                    },
                    "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                    "capacity": 25,
                    "demand": 0,
                    "location": {
                        "lec": "UP Alumni Engineers Centennial Hall",
                        "lab": "UP Alumni Engineers Centennial Hall",
                    },
                },
                {
                    "course_code": "CS 192",
                    "course_title": "Software Engineering II",
                    "section_name": {"lec": "TDE2", "lab": "TDE2/HUV2"},
                    "units": 3.0,
                    "timeslots": {"T": [180, 1020], "H": [180, 360]},
                    "class_days": {"lec": "T", "lab": "H"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lec": "SOLAMO, MA. ROWENA",
                        "lab": "SOLAMO, MA. ROWENA",
                    },
                    "venue": {"lec": "AECH-CLR2", "lab": "AECH-CLR2"},
                    "capacity": 25,
                    "demand": 0,
                    "location": {
                        "lec": "UP Alumni Engineers Centennial Hall",
                        "lab": "UP Alumni Engineers Centennial Hall",
                    },
                },
                {
                    "course_code": "CS 192",
                    "course_title": "Software Engineering II",
                    "section_name": {"lec": "TGI", "lab": "TGI/HWX"},
                    "units": 3.0,
                    "timeslots": {"T": [360, 480], "H": [360, 540]},
                    "class_days": {"lec": "T", "lab": "H"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lec": "SOLAMO, MA. ROWENA",
                        "lab": "SOLAMO, MA. ROWENA",
                    },
                    "venue": {"lec": "AECH-CLR2", "lab": "AECH-CLR2"},
                    "capacity": 25,
                    "demand": 0,
                    "location": {
                        "lec": "UP Alumni Engineers Centennial Hall",
                        "lab": "UP Alumni Engineers Centennial Hall",
                    },
                },
            ],
            [
                {
                    "course_code": "CS 194",
                    "course_title": "Undergraduate Research Seminar",
                    "section_name": {"lec": "MK"},
                    "units": 1.0,
                    "timeslots": {"M": [600, 660]},
                    "class_days": {"lec": "M"},
                    "offering_unit": "DCS",
                    "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                    "venue": {"seminar": "AECH-Accenture Rm"},
                    "capacity": 95,
                    "demand": 0,
                    "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                }
            ],
        ]

    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_generate_permutation_view(self):
        request = self.factory.get(reverse("homepage_view"))
        self.add_session_to_request(request)
        request.session["dcp_sections"] = self.dcp_sections
        request.user = self.user

        response = generate_permutation_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("homepage_view"))

        expected_permutations = [
            {
                "sched_id": 0,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TBC1", "lab": "TBC1/HQR1"},
                        "units": 3.0,
                        "timeslots": {"lec": (0, 180), "lab": (60, 180)},
                        "class_days": {"lab": "H", "lec": "T"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lab": "FIGUEROA, LIGAYA LEAH",
                            "lec": "FIGUEROA, LIGAYA LEAH",
                        },
                        "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                        "capacity": 25,
                        "demand": 0,
                        "location": {
                            "lab": "UP Alumni Engineers Centennial Hall",
                            "lec": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            },
            {
                "sched_id": 1,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TBC2", "lab": "TBC2/HQR2"},
                        "units": 3.0,
                        "timeslots": {"lec": (0, 180), "lab": (60, 180)},
                        "class_days": {"lab": "H", "lec": "T"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lab": "SOLAMO, MA. ROWENA",
                            "lec": "SOLAMO, MA. ROWENA",
                        },
                        "venue": {"lec": "AECH-CLR2", "lab": "AECH-CLR2"},
                        "capacity": 33,
                        "demand": 0,
                        "location": {
                            "lab": "UP Alumni Engineers Centennial Hall",
                            "lec": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            },
            {
                "sched_id": 2,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TDE1", "lab": "TDE1/HUV1"},
                        "units": 3.0,
                        "timeslots": {"lec": (180, 1020), "lab": (180, 360)},
                        "class_days": {"lec": "T", "lab": "H"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lec": "FIGUEROA, LIGAYA LEAH",
                            "lab": "FIGUEROA, LIGAYA LEAH",
                        },
                        "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                        "capacity": 25,
                        "demand": 0,
                        "location": {
                            "lec": "UP Alumni Engineers Centennial Hall",
                            "lab": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            },
            {
                "sched_id": 3,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TDE2", "lab": "TDE2/HUV2"},
                        "units": 3.0,
                        "timeslots": {"lec": (180, 1020), "lab": (180, 360)},
                        "class_days": {"lec": "T", "lab": "H"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lec": "SOLAMO, MA. ROWENA",
                            "lab": "SOLAMO, MA. ROWENA",
                        },
                        "venue": {"lec": "AECH-CLR2", "lab": "AECH-CLR2"},
                        "capacity": 25,
                        "demand": 0,
                        "location": {
                            "lec": "UP Alumni Engineers Centennial Hall",
                            "lab": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            },
            {
                "sched_id": 4,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TGI", "lab": "TGI/HWX"},
                        "units": 3.0,
                        "timeslots": {"lec": (360, 480), "lab": (360, 540)},
                        "class_days": {"lec": "T", "lab": "H"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lec": "SOLAMO, MA. ROWENA",
                            "lab": "SOLAMO, MA. ROWENA",
                        },
                        "venue": {"lec": "AECH-CLR2", "lab": "AECH-CLR2"},
                        "capacity": 25,
                        "demand": 0,
                        "location": {
                            "lec": "UP Alumni Engineers Centennial Hall",
                            "lab": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            },
        ]

        self.assertEqual(
            request.session["schedule_permutations"], expected_permutations
        )


User = get_user_model()


class ViewSavedSchedViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="TestingLebronJames",
            password="LebronJames123",
            email="LukaTroncic@gmail.com",
        )
        self.dcp_sections = [
            [
                {
                    "course_code": "CS 192",
                    "section_name": {"lec": "TDE1", "lab": "TDE1/HUV1"},
                    "units": 3.0,
                    "timeslots": {"lec": (180, 1020), "lab": (180, 360)},
                    "class_days": {"lec": "T", "lab": "H"},
                    "offering_unit": "DCS",
                    "instructor_name": {
                        "lec": "FIGUEROA, LIGAYA LEAH",
                        "lab": "FIGUEROA, LIGAYA LEAH",
                    },
                    "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                    "capacity": 25,
                    "demand": 0,
                    "location": {
                        "lec": "UP Alumni Engineers Centennial Hall",
                        "lab": "UP Alumni Engineers Centennial Hall",
                    },
                }
            ],
            [
                {
                    "course_code": "CS 194",
                    "section_name": {"lec": "MK"},
                    "units": 1.0,
                    "timeslots": {"lec": (600, 660)},
                    "class_days": {"lec": "M"},
                    "offering_unit": "DCS",
                    "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                    "venue": {"lec": "AECH-Accenture Rm"},
                    "capacity": 95,
                    "demand": 0,
                    "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                }
            ],
        ]

    def add_session_to_request(self, request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

    def test_view_sched_view_save_schedule(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["schedule_permutations"] = [
            {
                "sched_id": 2,
                "courses": (
                    {
                        "course_code": "CS 192",
                        "section_name": {"lec": "TDE1", "lab": "TDE1/HUV1"},
                        "units": 3.0,
                        "timeslots": {"lec": (180, 1020), "lab": (180, 360)},
                        "class_days": {"lec": "T", "lab": "H"},
                        "offering_unit": "DCS",
                        "instructor_name": {
                            "lec": "FIGUEROA, LIGAYA LEAH",
                            "lab": "FIGUEROA, LIGAYA LEAH",
                        },
                        "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                        "capacity": 25,
                        "demand": 0,
                        "location": {
                            "lec": "UP Alumni Engineers Centennial Hall",
                            "lab": "UP Alumni Engineers Centennial Hall",
                        },
                    },
                    {
                        "course_code": "CS 194",
                        "section_name": {"lec": "MK"},
                        "units": 1.0,
                        "timeslots": {"lec": (600, 660)},
                        "class_days": {"lec": "M"},
                        "offering_unit": "DCS",
                        "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                        "venue": {"lec": "AECH-Accenture Rm"},
                        "capacity": 95,
                        "demand": 0,
                        "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
                    },
                ),
            }
        ]
        session.save()

        response = self.client.post(
            reverse("view_sched_view", args=[2]), {"click_saved_sched": "Save Schedule"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("homepage_view"))

        saved_schedule = SavedSchedule.objects.filter(
            student_id=self.user.id, sched_id=2
        ).first()
        self.assertIsNotNone(saved_schedule)
        self.assertEqual(saved_schedule.schedule_name, "Sched 3")

        saved_courses = saved_schedule.courses.all()
        self.assertEqual(len(saved_courses), 2)
        self.assertEqual(saved_courses[0].course_code, "CS 192")
        self.assertEqual(saved_courses[1].course_code, "CS 194")

    def test_view_saved_sched_view(self):
        # First, save a schedule
        saved_schedule = SavedSchedule.objects.create(
            student_id=self.user.id, sched_id=2, schedule_name="Sched 3", is_saved=True
        )
        saved_course_1 = SavedCourse.objects.create(
            student_id=self.user.id,
            course_code="CS 192",
            course_details={
                "course_code": "CS 192",
                "section_name": {"lec": "TDE1", "lab": "TDE1/HUV1"},
                "units": 3.0,
                "timeslots": {"lec": (180, 1020), "lab": (180, 360)},
                "class_days": {"lec": "T", "lab": "H"},
                "offering_unit": "DCS",
                "instructor_name": {
                    "lec": "FIGUEROA, LIGAYA LEAH",
                    "lab": "FIGUEROA, LIGAYA LEAH",
                },
                "venue": {"lec": "AECH-CLR1", "lab": "AECH-CLR1"},
                "capacity": 25,
                "demand": 0,
                "location": {
                    "lec": "UP Alumni Engineers Centennial Hall",
                    "lab": "UP Alumni Engineers Centennial Hall",
                },
            },
        )
        saved_course_2 = SavedCourse.objects.create(
            student_id=self.user.id,
            course_code="CS 194",
            course_details={
                "course_code": "CS 194",
                "section_name": {"lec": "MK"},
                "units": 1.0,
                "timeslots": {"lec": (600, 660)},
                "class_days": {"lec": "M"},
                "offering_unit": "DCS",
                "instructor_name": {"lec": "VILLAR, JOHN JUSTINE"},
                "venue": {"lec": "AECH-Accenture Rm"},
                "capacity": 95,
                "demand": 0,
                "location": {"seminar": "UP Alumni Engineers Centennial Hall"},
            },
        )
        saved_schedule.courses.add(saved_course_1, saved_course_2)

        # Now, test accessing the saved schedule
        self.client.force_login(self.user)
        response = self.client.get(reverse("view_saved_sched_view", args=[2]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_sched.html")

        context = response.context
        self.assertEqual(context["sched_id"], 2)
        self.assertEqual(context["schedule_name"], "Sched 3")
        self.assertEqual(len(context["courses"]), 2)
        self.assertEqual(context["courses"][0].course_code, "CS 192")
        self.assertEqual(context["courses"][1].course_code, "CS 194")
        self.assertTrue(context["show_unsave_button"])
