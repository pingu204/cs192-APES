from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


"""
Custom manager for Student
Code (c) https://testdriven.io/blog/django-custom-user-model/
"""


class StudentManager(BaseUserManager):
    """
    Create a student with email as primary key
    """

    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)  # for case insensitivity
        user = self.model(
            email=email,
            username=username,
            **extra_fields,  # exists if called by `create_superuser`
        )
        user.set_password(password)
        user.save()
        return user

    """
    Create an admin
    """

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        # print(extra_fields.get("is_staff"))
        # print(extra_fields.get("is_active"))
        # print(extra_fields.get("is_superuser"))
        # print("hello?")
        return self.create_user(email, username, password, **extra_fields)
