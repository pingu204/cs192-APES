"""
User-defined utility functions used for the APES project.

This includes user-defined entities aimed to optimize project processes.
"""

from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def redirect_authenticated_users(view_function):
    """ Redirects logged-in users to the homepage /home/ route if the view/HTML page encapsulated in the view_function is accessed """
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("homepage_view"))
        return view_function(request, *args, **kwargs)
    
    return wrapper

def guest_or_authenticated(view_function):
    """ Allows access to authenticated (logged-in) users and guest accounts """
    @wraps(view_function)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get('is_guest', False): # allows both authenticated users and guests
            return view_function(request, *args, **kwargs)
        return redirect(reverse("login_view"))
    return wrapper