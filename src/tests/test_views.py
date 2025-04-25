# This Test is to test the VIEWS to the pages work
# -------------------------------------------------------------------------------

from django.test import TestCase, Client
from django.urls import reverse
from session.models import Student


class TestViewsNotGuest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register_view")
        self.login_url = reverse("login_view")

    def test_register_POST(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser",
                "password1": "Firsttimewelinkiwasaplayer123",
                "password2": "Firsttimewelinkiwasaplayer123",
                "email": "posttest@gmail.com",
                "agreement": True,
            },
        )
        self.assertEqual(response.status_code, 302)  # assuming a redirect
        self.assertTrue(Student.objects.filter(username="testuser").exists())

    def test_login_POST(self):
        # First, create a user to log in
        Student.objects.create_user(
            username="testuser",
            password="Iunderstanditnow123",
            email="test@example.com",
        )

        response = self.client.post(
            self.login_url, {"username": "testuser", "password": "Iunderstanditnow123"}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a redirect on successful login
        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )  # Assuming User is successfully logged in


class TestViewsGuest(TestCase):
    def setUp(self):
        self.client = Client()
        self.guest_login_url = reverse("guest_login_view")

    def test_guest_login(self):
        response = self.client.post(self.guest_login_url)
        self.assertEqual(response.status_code, 302)  # Assuming a redirect to homepage
        self.assertRedirects(response, reverse("homepage_view"))
        self.assertTrue(
            self.client.session.get("is_guest", False)
        )  # Check if 'is_guest' is set to True

    def test_logout_POST(self):
        # Log in as guest first
        self.client.post(self.guest_login_url)
        self.assertTrue(
            self.client.session.get("is_guest", False)
        )  # Ensure guest login

        # Log out
        guest_logout_url = reverse("logout_view")
        response = self.client.post(guest_logout_url)
        self.assertEqual(
            response.status_code, 302
        )  # Assuming a redirect to landing view
        self.assertRedirects(response, reverse("landing_view"))
        self.assertFalse(
            self.client.session.get("is_guest", False)
        )  # Ensure 'is_guest' is removed
