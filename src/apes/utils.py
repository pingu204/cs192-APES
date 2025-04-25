"""
User-defined utility functions used for the APES project.

This includes user-defined entities aimed to optimize project processes.
"""

import os
import csv
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


def redirect_authenticated_users(view_function):
    """Redirects logged-in users to the homepage /home/ route if the view/HTML page encapsulated in the view_function is accessed"""

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("homepage_view"))
        return view_function(request, *args, **kwargs)

    return wrapper


def guest_or_authenticated(view_function):
    """Allows access to authenticated (logged-in) users and guest accounts"""

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get(
            "is_guest", False
        ):  # allows both authenticated users and guests
            return view_function(request, *args, **kwargs)
        return redirect(reverse("login_view"))

    return wrapper


def get_course_details_from_csv(course_codes):
    """
    Reads courses.csv and returns a list of courses matching the given course_codes.
    """
    csv_path = os.path.join(settings.BASE_DIR, "scraper", "csv", "courses.csv")
    matched_courses = []

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if row["course_code"].strip() in course_codes:
                matched_courses.append(
                    {
                        "course_code": row["course_code"].strip(),
                        "course_title": row["course_title"].strip(),
                        "offering_unit": row["offering_unit"].strip(),
                        "units": float(row["units"]),
                        # ow["timeslot"].strip(),
                        # "venue": row["venue"].strip(),
                        # "instructor": row["instructor"].strip(),
                    }
                )

    return matched_courses


# print(get_course_details_from_csv(['CS 11', 'Physics 71']))
