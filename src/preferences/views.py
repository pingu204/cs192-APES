from django.shortcuts import render
from .forms import PreferencesForm, time_choices

# Create your views here.
def modify_preferences_view(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            number_of_classes = form.cleaned_data['number_of_classes']
            class_days = form.cleaned_data['class_days']
            total_distance_per_day = form.cleaned_data['total_distance_per_day']
            total_probability = form.cleaned_data['total_probability']

            # actual earliest time for DISPLAY (HTML, i.e., "7:30PM")
            earliest_time_val = form.cleaned_data['earliest_time']

            # actual latest time for DISPLAY (HTML, i.e., "7:30AM")
            latest_time_val = form.cleaned_data['latest_time']

            earliest_time_raw = next((i for i, (val, _) in enumerate(time_choices) if val == earliest_time_val), None)
            latest_time_raw = next((i for i, (val, _) in enumerate(time_choices) if val == latest_time_val), None)

            # value of earliest_time in MINUTES past 7:00 AM
            earliest_time = ((earliest_time_raw * 15) - 15) if earliest_time_raw else None

            # value of latest_time in MINUTES past 7:00 AM
            latest_time = ((latest_time_raw * 15) - 15) if latest_time_raw else None

            min_break_raw = form.cleaned_data.get('min_break') or 0
            min_unit_raw = form.cleaned_data.get('min_break_unit')
            min_unit = int(min_unit_raw) if min_unit_raw else 0

            # value of min_break duration in MINUTES PAST 7:00 AM
            min_break = min_break_raw * min_unit

            max_break_raw = form.cleaned_data.get('max_break') or 0
            max_unit_raw = form.cleaned_data.get('max_break_unit')
            max_unit = int(max_unit_raw) if max_unit_raw else 0

            # value of max_break duration in MINUTES PAST 7:00 AM
            max_break = max_break_raw * max_unit

            print("TEST PREFORMS TYPES")
            print(type(number_of_classes))
            print(type(class_days))
            print(type(total_distance_per_day))
            print(type(total_probability))
            print(type(earliest_time))
            print(type(latest_time))
            print(type(min_break))    
            print(type(max_break))
            print("END TEST PREFORMS TYPES")

            print("TEST PREFORMS")
            print(number_of_classes)
            print(class_days)
            print(total_distance_per_day)
            print(total_probability)
            print(earliest_time)
            print(latest_time)
            print(min_break)    
            print(max_break)
            #print(f"\n{earliest_time_val}")
            #print(f"\n{latest_time_val}")
            print("END TEST PREFORMS")

            print(request.session.keys())

            request.session['preferences'] = {
                'number_of_classes': number_of_classes if number_of_classes else None,
                'class_days': class_days if class_days else None,
                'total_distance_per_day': total_distance_per_day if total_distance_per_day else None,
                'total_probability': total_probability if total_probability else None,
                'earliest_time': earliest_time if earliest_time else None,
                'latest_time': latest_time if latest_time else None,
                'min_break': min_break if min_break else None,
                'max_break': max_break if max_break else None,
                'earliest_time_val': earliest_time_val if earliest_time_val else None, 
                'latest_time_val': latest_time_val if latest_time_val else None,
            }

        else:
            print(form.errors)
    
        print(request.session['preferences'].values())

    else:
        # not just GET later on... will load the values onto HTML...
        print("GET request; forms")
        form = PreferencesForm()


    context = {
        "form": form,
   
    }

    return render(request, "preferences.html", context)