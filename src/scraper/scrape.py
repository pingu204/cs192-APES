from bs4 import BeautifulSoup
import requests
import os

import string
import re
import pandas as pd

from enum import IntEnum

""" Parses HTML Website and Returns `tag` Elements """
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


""" Parses course code from `td` element """
def get_course_code(raw_code: str):
    # Only extract first line of the element in case of multi-line course codes
    # -- e.g. Bioinfo 297 HQR<br/>Computational Phylogenetics should be 'Bioinfo 297 HQR'
    course_code = raw_code.split("\n")[0]

    # Get index of course number, which will serve as the marker
    # -- e.g.
    # -- 'Bioinfo 297 HQR'      -> index 1
    # -- 'App Physics 101 THV'  -> index 2

    # -- Edge case: Courses w/o a course number
    no_course_number = ["Int", "Spec"]

    idx = 0 if course_code.split(" ")[0] not in no_course_number else -2

    for i, word in enumerate(course_code.split(" ")):
        if word[0].isnumeric():
            idx = i
            break

    # Obtain index offsets for special cases
    offset = 0

    # -- Initials of special courses
    one_suffix = ["CWTS", "LTS"]
    three_suffix = ["CWTS 1 and 2", "LTS 1 and 2"]
    variable_suffix = ["MuL", "MuP", "MuEd", "PE"]  # infer from length of code

    if True in [course_code.startswith(code) for code in variable_suffix]:
        offset = len(course_code.split(" ")) - 3
    elif True in [code in course_code for code in three_suffix]:
        offset = 3
    elif True in [code in course_code for code in one_suffix]:
        offset = 1

    # Slice the string until the marker
    course_code = " ".join(course_code.split(" ")[: idx + offset + 1])

    # Remove trailing spaces
    return course_code.rstrip()


def extract_section(raw_code: str, course_code: str):
    """
    Separates the section from `raw_code`
    """
    raw_code = raw_code.split("\n")[0]
    return raw_code[raw_code.index(course_code) + len(course_code) :].strip()

def convert_time(time_format: str) -> int:
    def get_offset(raw_time: str, is_afternoon: bool) -> int:
        # Normalize time string
        raw_time = raw_time if ":" in raw_time else raw_time + ":00"
        raw_time_split = raw_time.split(":")

        # Get hour value
        hour = int(raw_time_split[0]) + (12 if is_afternoon else 0)
        if int(raw_time_split[0]) == 12 and is_afternoon:
            hour = 12

        # Get minute value
        minute = int(raw_time_split[1])

        # Base time = 07:00 AM
        base = 7 * 60

        return ((hour * 60) + minute) - base

    start, end = 0, 0
    if "AM" in time_format.split("-")[0]:
        # Format: XXAM-XXPM
        start = get_offset(
            raw_time=(time_format.split("-")[0]).replace("AM", ""), is_afternoon=False
        )
        end = get_offset(
            raw_time=(time_format.split("-")[1]).replace("PM", ""), is_afternoon=True
        )
    else:
        # Format: XX-XXAM or XX-XXPM
        if "AM" in time_format.split("-")[1]:  # Morning Class
            start = get_offset(
                raw_time=(time_format.split("-")[0]).replace("AM", ""),
                is_afternoon=False,
            )
            end = get_offset(
                raw_time=(time_format.split("-")[1]).replace("AM", ""),
                is_afternoon=False,
            )
        else:  # Afternoon Class
            start = get_offset(
                raw_time=(time_format.split("-")[0]).replace("PM", ""),
                is_afternoon=True,
            )
            end = get_offset(
                raw_time=(time_format.split("-")[1]).replace("PM", ""),
                is_afternoon=True,
            )

    return (start, end)


""" Returns info about a section """
def get_timeslots(raw_sched_remarks: str):
    split_a = list(
        map(
            lambda x: x.strip(),  # Remove whitespace
            (raw_sched_remarks.split("\n"))[:-1],
        )
    )

    # Container for values
    timeslots: dict[str, str] = {}
    location: dict[str, str] = {}
    class_days: dict[str, str] = {}
    course_instructor: dict[str, str] = {}

    # Ignore erroneous schedules
    if split_a[1] == "TBA":
        return None, None, None

    for slot in split_a[1].split(";"):
        temp = slot.strip().split(" ", maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace("Th", "H"), temp[1], temp[2]

        if "lab" in slot_venue:
            class_days["lab"] = slot_days
            course_instructor["lab"] = split_a[2]
            timeslots["lab"] = convert_time(slot_time)
        elif "disc" in slot_venue:
            class_days["disc"] = slot_days
            course_instructor["disc"] = split_a[2]
            timeslots["disc"] = convert_time(slot_time)
        else:  # lec
            class_days["lec"] = slot_days
            course_instructor["lec"] = split_a[2]
            timeslots["lec"] = convert_time(slot_time)

    return timeslots, class_days, course_instructor


def map_venues(room: str, courses, cleaned_course_code):
    if "TBA" in room:
        if (
            (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "offering_unit"
                ].values[0]
            )
            == "GRADUATE"
        ):
            return (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "course_code"
                ].values[0]
            ).split()[0]
        else:
            return (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "offering_unit"
                ].values[0]
            ).split()[0]
    elif "Online" in room:
        return "Online"
    elif re.search("B[0-9]", room):
        return "Arch"
    elif re.search("[A-Z]{2,4}", room.split()[0]):
        if "AECH" in room:
            return "AECH"
        else:
            return room.split()[0]
    elif "Room" in room or "room" in room:
        if (
            (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "offering_unit"
                ].values[0]
            )
            == "GRADUATE"
        ):
            return (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "course_code"
                ].values[0]
            ).split()[0]
        else:
            return (
                courses.loc[
                    courses["course_code"] == cleaned_course_code, "offering_unit"
                ].values[0]
            ).split()[0]
    else:
        return room


def get_locations(raw_sched_remarks: str, course_code_csv, cleaned_course_code):
    split_a = list(
        map(
            lambda x: x.strip(),  # Remove whitespace
            (raw_sched_remarks.split("\n"))[:-1],
        )
    )

    # Ignore erroneous schedules
    if split_a[1] == "TBA":
        return None

    location: dict[str, str] = {}

    # load csv of rooms mapped to venues, in csv/venues_mapped.csv
    csv_file_path = os.path.join(
        os.path.dirname(__file__), "../scraper/csv/venues_mapped.csv"
    )
    df = pd.read_csv(csv_file_path, index_col=0)
    # print(df)

    for slot in split_a[1].split(";"):
        temp = slot.strip().split(" ", maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace("Th", "H"), temp[1], temp[2]
        room = (slot_venue.split(" ", maxsplit=1))[1]
        # print(room)
        # print('mapped: ', map_venues(room, course_code_csv,cleaned_course_code))
        mapped_venue = map_venues(room, course_code_csv, cleaned_course_code)
        # print('room: ', room, 'mapped: ', mapped_venue)
        if df.loc[df["code"] == mapped_venue, "location"].values:
            venue = df.loc[df["code"] == mapped_venue, "location"].values[0]
        else:
            venue = None
        # print(venue)
        # venue = df.loc[df['code'] == mapped_venue, 'location'].values[0]

        if "lab" in slot_venue:
            location["lab"] = venue
        elif "disc" in slot_venue:
            location["disc"] = venue
        else:
            location["lec"] = venue

    return location


def get_venues(raw_sched_remarks: str):
    split_a = list(
        map(
            lambda x: x.strip(),  # Remove whitespace
            (raw_sched_remarks.split("\n"))[:-1],
        )
    )

    # Ignore erroneous schedules
    if split_a[1] == "TBA":
        return None

    venues: dict[str, str] = {}
    for slot in split_a[1].split(";"):
        temp = slot.strip().split(" ", maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace("Th", "H"), temp[1], temp[2]
        room = (slot_venue.split(" ", maxsplit=1))[1]

        if "lab" in slot_venue:
            venues["lab"] = room
        elif "disc" in slot_venue:
            venues["disc"] = room
        else:
            venues["lec"] = room

    return venues

def get_info_from_csv(course_code: str):
    """
    Returns the following information about a course, given its `course_code`
    - Course Code
    - Course Title
    - Offering Unit
    - # of Units
    """

    # Load CSV
    csv_file_path = os.path.join(
        os.path.dirname(__file__), "../scraper/csv/courses.csv"
    )
    courses = pd.read_csv(csv_file_path, sep=",")

    # Return entry matching the course code
    return courses.loc[courses["course_code"] == course_code]


class Semester(IntEnum):
    FIRST = 1
    SECOND = 2
    MIDYEAR = 4

def extract_section_names(class_days:dict, raw_section_name):
    """
    Extracts the section names of a class
    """

    class_types = list(class_days.keys())
    
    # Check if class has both lecture and lab component
    if "lec" in class_types and "lab" in class_types:
        return {
            # -- Format: <course code> <lec section>/<lab section>
            "lec": raw_section_name.split("/")[0],
            "lab": raw_section_name,
        }
    else:
        return {
            "lec" if "lab" not in class_types
            else "lab" : raw_section_name,
        }


""" Get all sections of `course_code` """
def scrape_sections(year:int, sem:Semester, course_code:str, strict:bool = False):
    BASE_URL = "https://crs.upd.edu.ph/schedule/120" + str(year%100) + str(sem) + "/"
    print(BASE_URL)
    # Container for values
    courses = []

    # Scrape from URL
    soup = parse_html(BASE_URL + course_code.replace(" ", "%20"), "tr")

    for row in soup[1:]:  # Actual entries of the table start at index 1
        tr = row.find_all("td")

        if len(tr) < 7:
            continue

        # Check if there are no classes
        if tr[0].text != "No classes to display":
            cleaned_course_code = get_course_code(tr[1].get_text(separator="\n"))
            raw_capacity = tr[5].get_text(separator="\n").strip().split("/")

            # Check if scraped class must be strictly equal to the course code
            if strict and cleaned_course_code.lower() != course_code.lower():
                continue
            # Check if class is already dissolved
            elif raw_capacity[0].strip(" \n") == "DISSOLVED":
                continue
            
            raw_section_name =  extract_section(tr[1].get_text(separator="\n"), cleaned_course_code)
            course_timeslot, course_class_days, course_instructor = get_timeslots(tr[3].text)

            # Check if timeslot is not 'TBA' and that class was not dissolved ('X')
            if not (course_timeslot and raw_section_name != "X"):
                continue
                
            # Get course information from CSV
            course_code_csv = get_info_from_csv(cleaned_course_code)  # guaranteed to be unique!
            # print(cleaned_course_code, course_code_csv)
            # Separate course information
            course_title =         course_code_csv["course_title"].values[0]
            course_weight =        course_code_csv["units"].values[0]
            course_demand =        int(tr[6].text)
            course_capacity =      int(raw_capacity[1].strip(" \n\t"))
            course_location =      get_locations(tr[3].text, course_code_csv, cleaned_course_code)
            course_venue =         get_venues(tr[3].text)
            course_sections =      extract_section_names(course_class_days, raw_section_name)
            course_offering_unit = tr[4].text

            courses.append(
                {
                    "course_code":      cleaned_course_code,
                    "course_title":     course_title,
                    "section_name":     course_sections,
                    "units":            course_weight,
                    "timeslots":        course_timeslot,
                    "class_days":       course_class_days,
                    "offering_unit":    course_offering_unit,
                    "instructor_name":  course_instructor,
                    "venue":            course_venue,
                    "capacity":         course_capacity,
                    "demand":           course_demand,
                    "location":         course_location,
                }
            )

    return courses


def couple_lec_and_lab(lst):
    """
    Couples lab sections to their corresponding lecture sections
    """

    """ Checks if `x` is a standalone lab class"""
    def is_lab_section(x) -> bool:
        class_types = list(x["class_days"].keys())
        return "lab" in class_types and "lec" not in class_types

    """ Checks if `x` is a CS course """
    def is_cs_course(x) -> bool:
        return x["course_code"].startswith("CS")

    """ Returns lecture section of `course_to_check` if it exists in the stash """
    def find_lec_section(course_to_check, stash):
        return list(
            filter(
                lambda x: f"{x['course_code']} {x['section_name']['lec']}"
                == course_to_check, stash
            )
        )[:] 

    # Only get 'CS' sections with lab
    sections_with_lab = list(
        filter(lambda x: is_lab_section(x) and is_cs_course(x), lst)
    )

    # Get 'CS' sections without lab
    sections_without_lab = list(
        filter(lambda x: not (is_lab_section(x)) and is_cs_course(x), lst)
    )

    # Container for lec sections to be removed later
    to_remove = []

    # Loop through the lab sections
    for course in sections_with_lab:
        # Get the lec section -- Format: <course code> <lec section>/<lab section>
        code = course["course_code"]
        
        # Configure the section name
        if code == "CS 145":
            section = "HONOR" if "HONOR" in course["section_name"]["lab"] else "EXCELLENCE"
        else:
            section = course["section_name"]["lab"].split("/")[0]

        # Check if lec section was previously found
        lec_section = find_lec_section(f"{code} {section}", to_remove) 

        # Check if the lecture section was not previously found yet
        if not lec_section:
            lec_section = find_lec_section(f"{code} {section}", sections_without_lab)

        if lec_section:
            lec_section = lec_section[0]
        else:
            continue    # Lab section is standalone, proceed to next class

        # Obtain lecture fields from `lec_section`
        course["section_name"]["lec"] =     lec_section["section_name"]["lec"]
        course["class_days"]["lec"] =       lec_section["class_days"]["lec"]
        course["instructor_name"]["lec"] =  lec_section["instructor_name"]["lec"]
        course["timeslots"]["lec"] =        lec_section["timeslots"]["lec"]
        course["location"]["lec"] =         lec_section["location"]["lec"]
        course["venue"]["lec"] =            lec_section["venue"]["lec"]

        # Check if it's the first time that `lec_section` was found
        if lec_section not in to_remove:
            to_remove.append(lec_section)

    # Remove coupled lecture sections in `to_remove`
    for course in to_remove:
        lst.remove(course)

    return lst

def get_all_sections(year:int, sem:Semester, course_code:str, strict:bool = False):
    """
    Helper function that returns scraped sections with coupling handled
    """
    return couple_lec_and_lab(scrape_sections(year, sem, course_code, strict))

""" Prints a dictionary """
def print_dict(d):
    print("--")
    for key, value in d.items():
        print(f"+ {key} : {value}")


# *Every new sem, just update start_year and end_year for app updates (?)
if __name__ == "__main__":
    for x in get_all_sections(2025, Semester.FIRST, "cs 10", strict=True):
        print_dict(x)
