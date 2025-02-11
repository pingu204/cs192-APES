"""
Utility functions used for the APES project.

This includes user-defined entities aimed to optimize project processes.
"""

from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def redirect_authenticated_users(view_function):
    """ Redirects logged-in users to the homepage /home/ route if the view/HTML page encapsulated in the view_function is accessed"""
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("homepage_view"))
        return view_function(request, *args, **kwargs)
    
    return wrapper