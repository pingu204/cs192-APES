from django.shortcuts import render, redirect
from .forms import DesiredClassesForm
import csv
import os
from courses.models import Course
from django.forms.models import model_to_dict

# Create your views here.

def dcp_add_view(request):
    search_results = []
    form = DesiredClassesForm()

    if request.method == "POST":
        # Handle the POST request to save the class code
        course_code = request.POST.get("course_code")
        print("ADDED", course_code, "TO DCP")
        # Retrieve the current dcp from the session or initialize it if not present
        dcp = request.session.get('dcp', [])
        # Add the new course code to the dcp
        print ("coursecode:", course_code)
        csv_file_path = os.path.join(os.path.dirname(__file__), '../scraper/csv/courses.csv')
        with open(csv_file_path, newline='') as csvfile:
            
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # if it matches a class, then appends the whole description to search_results
                if course_code.upper() == row['course_code'].upper():
                    course = Course(
                        course_code=row['course_code'],
                        course_title=row['course_title'],
                        offering_unit=row['offering_unit'],
                        units=float(row['units']),
                        timeslot=row['timeslot'],
                        venue=row['venue'],
                        instructor=row['instructor']
                    )
                    
                    dcp.append(course)
                    print("added finally the dcp", row)
                    print("THIS IS DCP", dcp)
                    break
       
        # Update the session with the new dcp
        request.session['dcp'] = dcp
        
        return redirect('homepage_view')
    
    if request.GET.get("course_code"):
        print("searched")
        # get the raw query search placed by the user
        raw_search_query = request.GET["course_code"]
        # clean the raw search query such that spaces are resolved;
        cleaned_search_query = (' '.join(raw_search_query.split())).upper()

 
        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print(f"User's cleaned query: {cleaned_search_query}")
        
        csv_file_path = os.path.join(os.path.dirname(__file__), '../scraper/csv/courses.csv')

        # Open and read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # if it matches a class, then appends the whole description to search_results
                if cleaned_search_query == row['course_code'].upper():
                    search_results.append(row)
                    print(search_results)
                # wala pang no class found dito
                    

     

        # Now, we use this cleaned_search_query to match a course code! only EXACT MATCHING COURSE CODES
        # i.e. .startswith("course_code") can be used?
    
    else: # Normal Loading

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print("Enter DEFAULT /add/ routing")
        ...

    context = {
        "form" : form,
        "search_results" : search_results,
    }

    return render(request, "dcp_add.html", context)
