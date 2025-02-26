from bs4 import BeautifulSoup
import requests

import string

import pandas as pd

""" Parses HTML Website and Returns `tag` Elements """
def parse_html(url:str, tag:str):
    with requests.get(url) as page:
        soup = BeautifulSoup(page.text, "html.parser")
        return soup.find_all(tag)

""" Obtains all possible courses in CRS """
def get_courses() -> list[dict[str,str]]:
    BASE_URL = "https://crs.upd.edu.ph/course_catalog/index/"

    # Container for values
    courses: list[dict[str,str]] = []

    print(f"Scraping from {BASE_URL}...")
    
    # Get set of unique alphabet letters
    initials = list(string.ascii_lowercase)

    for letter in initials:
        # Obtain all rows of the table
        soup = parse_html(BASE_URL+letter, "tr")

        for row in soup[4:]: # Actual entries of the table start at index 4
            tr = row.find_all("td")
            # print(tr)

            # Check if there are no classes
            if (tr[0].text != "No courses to display"):
                courses.append(
                    {
                        "course_code" :     tr[0].text,
                        "course_title" :    tr[1].text,
                        "offering_unit" :   tr[3].text,
                    }
                )
        print(f"+ '{letter.capitalize()}' courses DONE")
        # print(courses)
    
    return pd.DataFrame(courses)

""" Parses course code from `td` element """
def get_course_code(raw_code: str):
    # Only extract first line of the element in case of multi-line course codes
    # -- e.g. Bioinfo 297 HQR<br/>Computational Phylogenetics should be 'Bioinfo 297 HQR'
    course_code = raw_code.split('\n')[0]

    # Remove section names
    # -- e.g. Bioinfo 297 HQR should be 'Bioinfo 297'
    course_code = ' '.join(course_code.split(' ')[:-1])

    # Remove trailing spaces
    return course_code.rstrip()

""" Obtain units of all courses in `course_codes` from A.Y. `start` to `end` """
def get_units_and_timeslot(start_year:int, end_year:int, course_codes:list[str]):
    # Note: start_year must be <= end_year
    # -- e.g. start_year = 2016, end_year = 2022 scrapes data from A.Y. 2016-2017 to A.Y. 2022-2023
    BASE_URL = "https://crs.upd.edu.ph/schedule/120"

    # Container for values
    units: dict[str, float] = {}
    timeslot: dict[str, str] = {}
    venue: dict[str, str] = {}
    instructor: dict[str, str] = {}

    len_courses = len(course_codes)

    # Get the last two digits of the years
    start_year %= 100
    end_year %= 100

    for year in range(end_year, start_year-1, -1):
        #for sem in [1, 2, 4]: # Semester Number (4 = Midyear)
        for sem in [2]:
            # Marker
            print(f"\n-- A.Y. {year}-{year+1}, " + (f"Sem {sem}" if sem != 4 else "Midyear") + " --")
            
            # Get unique initials of remaining course codes
            initials = list(set([word[0] for word in course_codes]))

            for letter in initials:
                # Obtain all rows of the table
                soup = parse_html(f"{BASE_URL}{year}{sem}/{letter}/", "tr")

                for row in soup[1:]: # Actual entries of the table start at index 1
                    tr = row.find_all("td")

                    # Check if there are no classes 
                    if (tr[0].text != "No classes to display"):
                        course_code = get_course_code(tr[1].get_text(separator='\n'))
                        
                        if course_code not in course_codes:
                            continue # Units for `course_code` already found; skip to next
                        else:
                            print(f"+ {course_code}")
                            units[course_code] = float(tr[2].text)

                            # instruction, timeslot, and venue processing
                            raw_sched_remarks = (tr[3].text)
                            split_a = (raw_sched_remarks.split("\n"))[:-1]
                            # DEBUGGING: print(split_a)

                            # print(split_a)

                            # If there are 2 time slots (and venues), separate the cases :)
                            if(';' in split_a[1]):
                                raw_time_venue_txt = (split_a[1].replace("\t", "")).split(";")
                                raw_tv_a, raw_tv_b = raw_time_venue_txt[0], raw_time_venue_txt[1]

                                raw_timeslot_a = " ".join(((raw_tv_a.strip()).split(" "))[:2])
                                raw_timeslot_b = " ".join(((raw_tv_b.strip()).split(" "))[:2])


                                raw_venue_a = " ".join(((raw_tv_a.strip()).split(" "))[3:])
                                raw_venue_b = " ".join(((raw_tv_b.strip()).split(" "))[3:])

                                raw_timeslot = raw_timeslot_a + "; " + raw_timeslot_b
                                raw_venue = raw_venue_a + "; " + raw_venue_b

                            else:
                                raw_timeslot = (" ".join((split_a[1].split(" "))[:2]).rstrip()).replace("\t", "")
                                raw_venue = (" ".join((split_a[1].split(" "))[3:]).rstrip()).replace("\t","")
                            
                            raw_instructor = (split_a[2]).replace("\t", "")

                            timeslot[course_code] = raw_timeslot
                            venue[course_code] = raw_venue
                            instructor[course_code] = raw_instructor

                            course_codes.remove(course_code)

            if course_codes == []:
                break

        if course_codes == []:
            break

        
    print(f"\n[Found: {len_courses - len(course_codes)}/{len_courses}]")

    return pd.DataFrame({
        "course_code" : list(units.keys()), 
        "units" :       list(units.values()),
        "timeslot" : list(timeslot.values()),
        "venue" : list(venue.values()),
        "instructor" : list(instructor.values()),
    })
    
def getting_all_sections(course_code: str):
    # URL to scrape, note that after 120, yearthensemester is the next.
    BASE_URL = "https://crs.upd.edu.ph/schedule/120242/"
    # Container for values
    courses: list[dict[str,str]] = []
    soup = parse_html(BASE_URL + course_code.replace(" ", "%20"), "tr")
    for row in soup[4:]: # Actual entries of the table start at index 4
        tr = row.find_all("td")
        # print(tr)

        # Check if there are no classes
        if (tr[0].text != "No courses to display"):
            courses.append(
                {
                    "course_code" :     tr[0].text,
                    "course_title" :    tr[1].text,
                    "course_units" :    tr[2].text,
                    "course_timeslot" :   tr[3].text,
                    "course_offeringunit" :   tr[4].text,
                }
            )
        
    print("courses DONE")
        # print(courses)
    
    return pd.DataFrame(courses)

def getting_section_details(course_code: str, course_title: str):
    
    BASE_URL = "https://crs.upd.edu.ph/schedule/120242/"
    # Container for values
    courses: list[dict[str,str]] = []
    soup = parse_html(BASE_URL + course_title.replace(" ", "%20"), "tr")
    for row in soup[4:]: # Actual entries of the table start at index 4
        tr = row.find_all("td")
        # print(tr)
        print("COURSE CODE", course_code)
        print("TR[1]", tr[0].text)
        # Check if there are no classes
        if (tr[0].text != "No courses to display" and tr[0].text == course_code):
            print("FOUND")
            course_timeslot = (tr[3].text).split("\n\t\t\t")
            print("course timeslot:", course_timeslot)
            course_timeslot = course_timeslot[1].strip()
            print("course timeslot:", course_timeslot)
            course_timeslot = (course_timeslot.split(" ", 2))
            print("course timeslot:", course_timeslot)
            
            
            courses.append(
                {
                    "course_code" :     tr[0].text,
                    "course_title" :    tr[1].text,
                    "course_units" :    tr[2].text,
                    "course_timeslot" :   course_timeslot[1],
                    "course_offeringunit" :   tr[4].text,
                    "venue" : course_timeslot[1],
                    "instructor" : course_timeslot[2]
                    
                }
            )
            print(courses)
    # Container for values
    units: dict[str, float] = {}
    timeslot: dict[str, str] = {}
    venue: dict[str, str] = {}
    instructor: dict[str, str] = {}
    len_courses = len(course_code)

   

    return pd.DataFrame({
        "course_code" : list(units.keys()), 
        "units" :       list(units.values()),
        "timeslot" : list(timeslot.values()),
        "venue" : list(venue.values()),
        "instructor" : list(instructor.values()),
    })

# *Every new sem, just update start_year and end_year for app updates (?)
if __name__ == "__main__":
    course_list = get_courses()
    print(course_list)

    units_list = get_units_and_timeslot(
        start_year =    2024,
        end_year =      2024, 
        course_codes =  list(set(course_list["course_code"].tolist()))[:],
    )
    print(units_list)

    course_list_with_units = course_list.merge(units_list, on="course_code", how="left")
    print(course_list_with_units)
    course_list_with_units.dropna(subset='units', inplace=True)
    course_list_with_units.to_csv("csv/courses.csv", index=False)