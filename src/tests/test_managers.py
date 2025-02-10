from django.contrib.auth import get_user_model
from django.test import TestCase


class UsersManagersTests(TestCase):
    ## errro
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", username="imnormal", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertEqual(user.username, "imnormal")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        
        with self.assertRaises(TypeError):
            User.objects.create_user()

        with self.assertRaises(ValueError):
            User.objects.create_user(email="", username="imnormal", password="foo")
    ##error
    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email="super@user.com",username="imadmin", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertEqual(admin_user.username, "imadmin")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        