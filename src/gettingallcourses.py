from bs4 import BeautifulSoup
import requests

import string

import pandas as pd


def parse_html(url: str, tag: str):
    with requests.get(url) as page:
        soup = BeautifulSoup(page.text, "html.parser")
        return soup.find_all(tag)


""" Obtains all possible courses in CRS """


def get_courses() -> list[dict[str, str]]:
    BASE_URL = "https://crs.upd.edu.ph/course_catalog/index/"

    # Container for values
    courses: list[dict[str, str]] = []

    print(f"Scraping from {BASE_URL}...")

    # Get set of unique alphabet letters
    initials = list(string.ascii_lowercase)

    for letter in initials:
        # Obtain all rows of the table
        soup = parse_html(BASE_URL + letter, "tr")

        for row in soup[4:]:  # Actual entries of the table start at index 4
            tr = row.find_all("td")
            # print(tr)

            # Check if there are no classes
            if tr[0].text != "No courses to display":
                courses.append(
                    {
                        "course_code": tr[0].text,
                        "course_title": tr[1].text,
                        "offering_unit": tr[3].text,
                    }
                )
        print(f"+ '{letter.capitalize()}' courses DONE")
        # print(courses)

    return pd.DataFrame(courses)


def getting_all_courses(course_code: str):
    # URL to scrape, note that after 120, yearthensemester is the next.
    BASE_URL = "https://crs.upd.edu.ph/schedule/120242/"
    # Container for values
    courses: list[dict[str, str]] = []
    soup = parse_html(BASE_URL + course_code.replace(" ", "%20"), "tr")
    for row in soup[4:]:  # Actual entries of the table start at index 4
        tr = row.find_all("td")
        print(tr)

        # Check if there are no classes
        if tr[0].text != "No courses to display":
            courses.append(
                {
                    "course_code": tr[0].text,
                    "course_title": tr[1].text,
                    "offering_unit": tr[3].text,
                }
            )
    print("courses DONE")
    # print(courses)

    return pd.DataFrame(courses)


print(getting_all_courses("Soc Sci 1"))


def create_class_view(request):
    search_results = []
    form = CreateClassForm(request.GET)

    if request.method == "POST":
        # Handle the POST request to save the class code
        print(request.POST.get("course_code"))

        course_code = request.POST.get("course_code")

        if request.user.id:
            # Obtain DCP from database
            dcp_codes = [
                x.course_code
                for x in list(DesiredCourse.objects.filter(student_id=request.user.id))
            ]
        else:  # Guest user
            # Obtain DCP from `request.session`
            dcp_codes = [x["course_code"] for x in request.session.get("dcp", [])]
            print(dcp_codes)

            # Obtain sections of classes in DCP
            dcp_sections = request.session.get("dcp_sections", [])

            if dcp_sections == []:  # Not cached yet
                dcp_sections = [
                    get_all_sections(code, strict=True) for code in dcp_codes
                ]
                request.session["dcp_sections"] = dcp_sections
                request.session.save()

            # Obtain sections of course to be added
            course_sections = list(
                filter(
                    lambda x: x["course_code"] == course_code,
                    request.session["course_sections"],
                )
            )

            timeout = False

            for section in course_sections:
                """Checks if `section`'s timeslots collides with `x`"""

                def is_not_within_range(x) -> bool:
                    course_days = set(list("".join(list(section["timeslot"].keys()))))
                    x_days = set(list("".join(list(x["timeslot"].keys()))))

                    for day in list(course_days.intersection(x_days)):
                        print(day)
                        course_start, course_end = get_start_and_end(
                            section["timeslot"], day
                        )
                        x_start, x_end = get_start_and_end(x["timeslot"], day)

                        if not (x_end <= course_start or x_start >= course_end):
                            return False

                    return True

                print("before filtering: ", sum([len(x) for x in dcp_sections]))

                temp = []

                # Pre-filter the DCP sections
                for i, section_lst in enumerate(dcp_sections):
                    temp.append(list(filter(is_not_within_range, section_lst)))

                print("after filtering: ", ([len(x) for x in temp]))

                for i, dcp_section in enumerate(list(product(*temp))):
                    if not is_conflicting([section] + list(dcp_section)):
                        print([section] + list(dcp_section))
                        if request.user.id:
                            DesiredCourse.objects.create(
                                student_id=request.user.id, course_code=course_code
                            )
                        else:
                            request.session["dcp"].append(course_sections[0])
                            request.session.save()

                        # Append current course's sections to DCP sections
                        request.session["dcp_sections"].append(course_sections)
                        request.session.save()
                        print(
                            f"Sessions's `dcp_sections` now has {len(request.session['dcp_sections'])} sections."
                        )

                        messages.success(request, "Class has been successfully added.")
                        return redirect(reverse("homepage_view"))

                    if i == 100000:
                        timeout = True
                        break

            if timeout:
                messages.error(request, "Couldn't complete request in time.")
            else:
                messages.error(request, "Class conflicts with another class.")

    elif request.GET.get("course_code"):
        form = DesiredClassesForm(request.GET)

        # Obtain the raw query text inputted by the user
        raw_search_query = request.GET["course_code"]

        # Clean the `raw_search_query` such that whitespaces are omitted
        cleaned_search_query = (" ".join(raw_search_query.split())).upper()

        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print(f"User's cleaned query: {cleaned_search_query}")

        csv_file_path = os.path.join(settings.BASE_DIR, "scraper", "csv", "courses.csv")

        if form.is_valid():
            # Obtain all sections associated with `raw_search_query` course code
            course_sections = get_all_sections(cleaned_search_query)

            request.session["course_sections"] = course_sections
            search_results = get_unique_courses(course_sections)

    else:  # Normal Loading
        # DEBUGGING: purely for testing only; omit or comment when unneeded
        print("Enter DEFAULT /add/ routing")
        ...

    context = {
        "form": form,
        "search_results": search_results,
    }

    return render(request, "dcp_add.html", context)
