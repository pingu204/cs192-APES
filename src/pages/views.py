from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from apes.utils import redirect_authenticated_users, guest_or_authenticated, get_course_details_from_csv
from django.contrib import messages
from courses.models import DesiredCourse, SavedSchedule
from courses.views import generate_permutation_view
from scraper.scrape import couple_lec_and_lab, get_all_sections
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

        request.session["dcp_sections"] = []
        request.session.save()

    if request.method == "POST" and "removed_course" in request.POST:
        removed_course_code = request.POST["removed_course"]

        if request.user.is_authenticated:
            print(f"{request.user} Removing {removed_course_code}")
            DesiredCourse.objects.filter(student_id=request.user.id, course_code=removed_course_code).delete()
        else:
            print(f"Guest removing {removed_course_code}")
            request.session["dcp"] = [course for course in request.session.get("dcp", []) if course["course_code"] != removed_course_code]

        request.session["dcp_sections"] = [section_lst for section_lst in request.session.get("dcp_sections", []) if section_lst[0]["course_code"] != removed_course_code]

        print(f"Session's `dcp_sections` now has {len(request.session["dcp_sections"])} sections.")
        
        messages.success(request, "Class has been successfully removed.")
        
    if request.method == "POST" and "generate_permutation" in request.POST:
        if 'dcp_sections' not in request.session or not request.session['dcp_sections']:
            messages.error(request, "No DCP sections found.")
            generate_permutation_view(request)
            # print("Crashout")  # Debugging
            # generate_permutation_view(request) # generate again to refresh the displayed permutations when GENERATE clicked again after CLEAR
            return redirect(reverse("homepage_view"))

        dcp_sections = request.session['dcp_sections']
        #print("DCP SECTIONS: ", dcp_sections)  # Debugging
        generate_permutation_view(request)

        # request.session.get('schedule_permutations')

    if request.user.id is None:  # Guest
        dcp = request.session.get("dcp", [])   
        print(dcp)
    else:  # Authenticated user
        desired_courses = DesiredCourse.objects.filter(student_id=request.user.id)
        course_codes = [dc.course_code for dc in desired_courses]
        dcp = get_course_details_from_csv(course_codes)
        #print("User dict", request.session['dcp_sections'])

    dcp_codes = [course["course_code"] for course in dcp]
    dcp_sections = request.session.get("dcp_sections", [])

    if dcp_sections == []: # Not cached yet
        dcp_sections = [couple_lec_and_lab(get_all_sections(code, strict=True)) for code in dcp_codes]
        request.session['dcp_sections'] = dcp_sections
        request.session.save()

    print("-- User DCP --")
    print('\n'.join([f"+ {code} [{len(dcp_sections[i])} sections]" for i, code in enumerate(dcp_codes)]))

    schedules = SavedSchedule.objects.filter(student_id=request.user.id).prefetch_related('courses')
    for sched in schedules:
        print(f"+++ {request.user} Saved Schedule: {sched.schedule_name}")  # Adjust based on actual field name
        for course in sched.courses.all():
            print(f"  - {course.course_code}")  # Ensure SavedCourse has a proper __str__ method

    context = {
        "user" : request.user,
        "dcp" : dcp,
        "dcp_units" : sum([course['units'] for course in dcp]),
        "dcp_length" : len(dcp),
        "saved_schedules" : SavedSchedule.objects.filter(student_id=request.user.id), 
        "session" : request.session,
    }

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
    # print(request.session.items())
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
