from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import StudentManager

class Student(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(max_length=20)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

    objects = StudentManager()

    def __str__(self):
        return self.email