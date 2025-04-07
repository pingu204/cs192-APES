from django.shortcuts import render
from .forms import PreferencesForm

# Create your views here.
def modify_preferences_view(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            number_of_classes = form.cleaned_data['number_of_classes']
            class_days = form.cleaned_data['class_days']
            total_distance_per_day = form.cleaned_data['total_distance_per_day']
            total_probability = form.cleaned_data['total_probability']
            earliest_time = form.cleaned_data['earliest_time']
            latest_time = form.cleaned_data['latest_time']
            min_break = form.cleaned_data['min_break']
            min_break_unit = form.cleaned_data['min_break_unit']
            max_break = form.cleaned_data['max_break']
            max_break_unit = form.cleaned_data['max_break_unit']

            print("TEST PREFORMS")
            print(number_of_classes)
            print(class_days)
            print(total_distance_per_day)
            print(total_probability)
            print(earliest_time)
            print(latest_time)
            print(min_break)    
            print(min_break_unit)
            print(max_break)
            print(max_break_unit)
            print("END TEST PREFORMS")
        else:
            print(form.errors)

    else:
        print("GET request; forms")
        form = PreferencesForm()


    context = {
        "form": form,
   
    }

    return render(request, "preferences.html", context)