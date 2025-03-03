from bs4 import BeautifulSoup
import requests
import os

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

    # Get index of course number, which will serve as the marker
    # -- e.g.
    # -- 'Bioinfo 297 HQR'      -> index 1
    # -- 'App Physics 101 THV'  -> index 2 
    idx = 0

    # Remove `.` in the course numbers
    for i, word in enumerate(course_code.replace('.', '').split(' ')):
        if word.isnumeric():
            idx = i
            break
    
    # Slice the string until the marker
    course_code = ' '.join(course_code.split(' ')[:idx+1])

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

                            # If there are 2 time slots (and location), separate the cases :)
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

def convert_time(time_format: str) -> int:
    def get_offset(raw_time: str, is_afternoon: bool) -> int:
        # Normalize time string
        raw_time = raw_time if ':' in raw_time else raw_time + ':00'
        raw_time_split = raw_time.split(':')

        # Get hour value
        hour = int(raw_time_split[0]) + (12 if is_afternoon else 0)

        # Get minute value
        minute = int(raw_time_split[1])

        # Base time = 07:00 AM
        base = 7*60 

        return ((hour*60) + minute) - base

    start, end = 0, 0
    if 'AM' in time_format.split('-')[0]:
        # Format: XXAM-XXPM
        start = get_offset(
            raw_time = (time_format.split('-')[0]).replace('AM',''),
            is_afternoon = False
        )
        end = get_offset(
            raw_time = (time_format.split('-')[1]).replace('PM',''),
            is_afternoon = True
        )
    else:
        # Format: XX-XXAM or XX-XXPM
        if 'AM' in time_format.split('-')[1]: # Morning Class
            start = get_offset(
                raw_time = (time_format.split('-')[0]).replace('AM',''),
                is_afternoon = False
            )
            end = get_offset(
                raw_time = (time_format.split('-')[1]).replace('AM',''),
                is_afternoon = False
            )
        else: # Afternoon Class
            start = get_offset(
                raw_time = (time_format.split('-')[0]).replace('PM',''),
                is_afternoon = True
            )
            end = get_offset(
                raw_time = (time_format.split('-')[1]).replace('PM',''),
                is_afternoon = True
            )
    
    return (start,end)
    

def get_timeslots(raw_sched_remarks: str):
    split_a = list(map(
        lambda x : x.strip(), # Remove whitespace
        (raw_sched_remarks.split("\n"))[:-1]
    ))

    # Container for values
    timeslots: dict[str,str] = {}
    location: dict[str,str] = {}
    class_days: dict[str,str] = {}

    # Ignore erroneous schedules
    if split_a[1] == "TBA":
        return None

    for slot in split_a[1].split(';'):
        temp = slot.strip().split(' ', maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0], temp[1], temp[2]

        timeslots[slot_days.replace('Th', 'H')] = convert_time(slot_time)
        if "lab" in slot_venue:
            class_days["lab"] = slot_days
            location["lab"] = slot_venue.replace("lab", "").strip()
        elif "disc" in slot_venue:
            class_days["disc"] = slot_days
            location["disc"] = slot_venue.replace("disc", "").strip()
        else: # lec
            class_days["lec"] = slot_days
            location["lec"] = slot_venue.replace("lec", "").strip()

    return timeslots

""" Get information about a course given its `course_code` """
def get_info_from_csv(course_code: str):
    csv_file_path = os.path.join(os.path.dirname(__file__), '../scraper/csv/courses.csv')
    courses = pd.read_csv(csv_file_path, sep=',')
    return courses.loc[courses['course_code'] == course_code]


""" Get all sections of `course_code` """    
def get_all_sections(course_code: str, strict: bool = False):
    # URL to scrape, note that after 120, yearthensemester is the next.
    #######################################################
    ## FOR FUTURE USE, REMOVE HARDCODING OF YEAR AND SEM ##
    #######################################################
    BASE_URL = "https://crs.upd.edu.ph/schedule/120242/"

    # Container for values
    courses = []

    # Scrape from URL
    print(course_code)
    soup = parse_html(BASE_URL + course_code.replace(" ", "%20"), "tr")

    for row in soup[1:]: # Actual entries of the table start at index 1
        tr = row.find_all("td")

        if len(tr) < 7:
            continue
        
        # Check if there are no classes
        if (tr[0].text != "No classes to display"):
            cleaned_course_code = get_course_code(tr[1].get_text(separator='\n'))

            # Check if scraped class must be strictly equal to the course code
            if strict and cleaned_course_code.lower() != course_code.lower():
                continue

            course_code_csv = get_info_from_csv(cleaned_course_code) # guaranteed to be unique!
            print(cleaned_course_code, course_code_csv)
            course_timeslot = get_timeslots(tr[3].text)

            if course_timeslot:
                courses.append(
                    {
                        "course_code" : cleaned_course_code,
                        "course_title" : course_code_csv['course_title'].values[0],
                        "units" : course_code_csv['units'].values[0],
                        "timeslot" : get_timeslots(tr[3].text),
                        "offeringunit" : tr[4].text,
                    }
                )
    
    return courses

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