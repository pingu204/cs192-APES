from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apes.utils import redirect_authenticated_users, guest_or_authenticated, get_course_details_from_csv

from courses.models import DesiredCourse, Course
# Create your views here.

@redirect_authenticated_users
def landing_view(request, *args, **kwargs):
    return render(request, "landing.html", {})

@guest_or_authenticated
def homepage_view(request, *args, **kwargs): 
    if request.method == "POST" and "clear_dcp" in request.POST:
        if request.user.is_authenticated:
            DesiredCourse.objects.filter(student_id=request.user.id).delete()
            print(f"User {request.user.id} DCP classes cleared!")
        else:
            request.session["dcp"] = []
            print("Guest DCP classes cleared!")

    if request.method == "POST" and "removed_course" in request.POST:
        removed_course_code = request.POST["removed_course"]

        if request.user.is_authenticated:
            print(f"{request.user} Removing {removed_course_code}")
            DesiredCourse.objects.filter(student_id=request.user.id, course_code=removed_course_code).delete()
        else:
            print(f"Guest removing {removed_course_code}")
            request.session["dcp"] = [course for course in request.session.get("dcp", []) if course["course_code"] != removed_course_code]
            


    # Wala pang confirmation message like: CLEAR -> "Are you sure you wanna do this?" -> Yes/No -> skibidi act upon Yes/No

    if request.user.id is None:  # Guest
        dcp = request.session.get("dcp", [])   
        print(dcp)
    else:  # Authenticated user
        desired_courses = DesiredCourse.objects.filter(student_id=request.user.id)
        course_codes = [dc.course_code for dc in desired_courses]
        dcp = get_course_details_from_csv(course_codes)
        

    context = {
        "user" : request.user,
        "dcp" : dcp,
        "dcp_units" : sum([course['units'] for course in dcp]),
        "dcp_length" : len(dcp),
    }

    #print("eto yon", request.user, request.user.id)
    #print("eto yon2xx",request.session.items())

    # DEBUGGER: print(context['user']) #prints AnonymousUser if guest
    # DEBUGGER: print(context['user'].username)
    return render(request, "homepage.html", context)


@require_POST # POST since user data gets saved during session; after session termination, flush user data
@redirect_authenticated_users
def guest_login_view(request, *args, **kwargs):
    """
    
    Ensure that only POST methods bypass; 
    if a guest login happens, an is_guest key in request.sessions.items() is added which has the value True
    so that, when the homepage is accessed, it defaults to the guest BUT this only happens when the user opted to sign in already as guest via the buttons in /login/ or /landing_view/
    however, if the user opts to login authentically via an existing account, the is_guest key gets popped and hence, the active user account takes over
    
    """
    # DEBUGGER: print("GUEST AUTHENTICATED")
    request.session['is_guest'] = True # might be useful if we choose to separate guest from user dashboards// if guest -> save session, else flush after
    request.session['dcp'] = [] # for Desired Classes Pool
    print(request.session.items())
    # DEBUGGER: print(request.session.keys())
    # DEBUGGER: print(request.session['is_guest'])
    return redirect(reverse('homepage_view'))

def logout_view(request, *args, **kwargs):
    # if POST method, ensures that users don't logout by simply rerouting to /logout/
    if request.method == 'POST':
        logout(request)

        request.session.flush()

        # messages.success(request, ("Successfully Logged Out.")) # optional (if we want to display an error message to the users, then just add here)
        return redirect(reverse("landing_view"))
    
    if request.user.is_authenticated:
        return redirect(reverse("homepage_view"))
    else:
        return redirect(reverse("landing_view"))
    

def database_error_view(request):
    error_message = request.session.pop('database_error', "Database connection failed. Please try again later.")
    return render(request, 'database_error.html', {'error': error_message}, status=500)

def clear_desired_courses(request):
    if request.method == "POST":

        if request.user.is_authenticated:
            DesiredCourse.objects.filter(student_id=request.user.id).delete()
            print("User DCP classes cleared!")

        else:
            request.session["dcp"] = []
            print("Guest DCP classes cleared!")

    return redirect(reverse("homepage_view"))