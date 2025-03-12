from bs4 import BeautifulSoup
import requests
import os

import string
import re
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

    # -- Edge case: Courses w/o a course number 
    no_course_number = ['Int','Spec']

    idx = 0 if course_code.split(' ')[0] not in no_course_number else -2

    for i, word in enumerate(course_code.split(' ')):
        if word[0].isnumeric():
            idx = i
            break

    # Obtain index offsets for special cases
    offset = 0

    # -- Initials of special courses
    one_suffix =        ['CWTS', 'LTS']
    three_suffix =      ['CWTS 1 and 2', 'LTS 1 and 2']
    variable_suffix =   ['MuL', 'MuP', 'MuEd', 'PE']    # infer from length of code

    if True in [course_code.startswith(code) for code in variable_suffix]:
        offset = len(course_code.split(' ')) - 3
    elif True in [code in course_code for code in three_suffix]:
        offset = 3
    elif True in [code in course_code for code in one_suffix]:
        offset = 1
    
    # Slice the string until the marker
    course_code = ' '.join(course_code.split(' ')[: idx + offset + 1])

    # Remove trailing spaces
    return course_code.rstrip()

def get_section(raw_code:str, course_code:str):
    raw_code = raw_code.split('\n')[0]
    return raw_code[raw_code.index(course_code) + len(course_code):].strip()

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
    
""" Returns info about a section """
def get_timeslots(raw_sched_remarks: str):
    split_a = list(map(
        lambda x : x.strip(), # Remove whitespace
        (raw_sched_remarks.split("\n"))[:-1]
    ))

    # Container for values
    timeslots: dict[str,str] = {}
    location: dict[str,str] = {}
    class_days: dict[str,str] = {}
    instructor_name: dict[str,str] = {}

    # Ignore erroneous schedules
    if split_a[1] == "TBA":
        return None

    for slot in split_a[1].split(';'):
        temp = slot.strip().split(' ', maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace('Th', 'H'), temp[1], temp[2]

        timeslots[slot_days] = convert_time(slot_time)
        if "lab" in slot_venue:
            class_days["lab"] = slot_days
            instructor_name["lab"] = split_a[2]
        elif "disc" in slot_venue:
            class_days["disc"] = slot_days
            instructor_name["disc"] = split_a[2]
        else: # lec
            class_days["lec"] = slot_days
            instructor_name["lec"] = split_a[2]

    return timeslots, class_days, instructor_name

def map_venues(room : str, courses, cleaned_course_code):
    if 'TBA' in room:
        if (courses.loc[courses['course_code'] == cleaned_course_code, 'offering_unit'].values[0]) == 'GRADUATE':
            return (courses.loc[courses['course_code'] == cleaned_course_code, 'course_code'].values[0]).split()[0]
        else:
            return (courses.loc[courses['course_code'] == cleaned_course_code, 'offering_unit'].values[0]).split()[0]
    elif 'Online' in room:
        return 'Online'
    elif re.search('B[0-9]', room):
        return 'Arch'
    elif re.search('[A-Z]{2,4}', room.split()[0]):
        if 'AECH' in room:
            return 'AECH'
        else:
            return room.split()[0]
    elif 'Room' in room or 'room' in room:
        if (courses.loc[courses['course_code'] == cleaned_course_code, 'offering_unit'].values[0]) == 'GRADUATE':
            return (courses.loc[courses['course_code'] == cleaned_course_code, 'course_code'].values[0]).split()[0]
        else:
            return (courses.loc[courses['course_code'] == cleaned_course_code, 'offering_unit'].values[0]).split()[0]
    else:
        return room

def get_locations(raw_sched_remarks: str, course_code_csv, cleaned_course_code):
    split_a = list(map(
        lambda x : x.strip(), # Remove whitespace
        (raw_sched_remarks.split("\n"))[:-1]
    ))

    location: dict[str,str] = {}

    # load csv of rooms mapped to venues, in csv/venues_mapped.csv
    csv_file_path = os.path.join(os.path.dirname(__file__), '../scraper/csv/venues_mapped.csv')
    df = pd.read_csv(csv_file_path, index_col=0)
    # print(df)
    
    for slot in split_a[1].split(';'):
        temp = slot.strip().split(' ', maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace('Th', 'H'), temp[1], temp[2]
        room = (slot_venue.split(' ', maxsplit=1))[1]
        # print(room)
        # print('mapped: ', map_venues(room, course_code_csv))
        mapped_venue = map_venues(room, course_code_csv, cleaned_course_code)
        print('room: ', room, 'mapped: ', mapped_venue)
        venue = df.loc[df['code'] == mapped_venue, 'location'].values[0]

        if 'lab' in slot_venue:
            location['lab'] = venue
        else:
            location[(slot_venue.split(' ', maxsplit=1))[0]] = venue
        
    return location

def get_venues(raw_sched_remarks: str):
    split_a = list(map(
        lambda x : x.strip(), # Remove whitespace
        (raw_sched_remarks.split("\n"))[:-1]
    ))

    venues : dict[str, str] = {}
    for slot in split_a[1].split(';'):
        temp = slot.strip().split(' ', maxsplit=2)
        slot_days, slot_time, slot_venue = temp[0].replace('Th', 'H'), temp[1], temp[2]
        room = (slot_venue.split(' ', maxsplit=1))[1]
        # print(room)

        if 'lab' in slot_venue:
            venues['lab'] = room
        else:
            venues[(slot_venue.split(' ', maxsplit=1))[0]] = room
    return venues

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
            section_name = get_section(tr[1].get_text(separator='\n'), cleaned_course_code)

            # Check if scraped class must be strictly equal to the course code
            if strict and cleaned_course_code.lower() != course_code.lower():
                continue

            course_code_csv = get_info_from_csv(cleaned_course_code) # guaranteed to be unique!
            # print(course_code_csv)
            # Get the course's
            # -- timeslot (dict)
            # -- class days (dict)
            # -- instructor name/s (dict)
            course_timeslot, course_class_days, instructor_name = get_timeslots(tr[3].text)
            # print('course_timeslot: ', course_timeslot)
            scrape_capacity = tr[5].get_text(separator='\n').strip().split('/')
            print(scrape_capacity)

# -- Check if class has been dissolved -> ignore
            if scrape_capacity[0].strip(' \n') == "DISSOLVED":
                continue
            demand = int(tr[6].text)
            print(demand)
            capacity = int(scrape_capacity[1].strip(' \n\t'))
            location = get_locations(tr[3].text, course_code_csv, cleaned_course_code)
            course_venue = get_venues(tr[3].text)
            # print(course_venue)
            # Check if timeslot is not 'TBA' and that class was not dissolved ('X')
            if course_timeslot and section_name != 'X':
                # Configure `section_name` field
                # -- Check if section is both a lec and lab section (e.g. CS 192)
                if "lec" in list(course_class_days.keys()) and "lab" in list(course_class_days.keys()):
                    section_name = {
                        # -- Format: <course code> <lec section>/<lab section>
                        "lec" : section_name.split('/')[0], 
                        "lab" : section_name,
                    }
                else:
                    # -- Section is a standalone course
                    section_name = {
                        "lec" if "lab" not in list(course_class_days.keys()) else "lab": section_name,
                    }

                courses.append(
                    {
                        "course_code" :     cleaned_course_code,
                        "course_title" :    course_code_csv['course_title'].values[0],
                        "section_name" :    section_name,
                        "units" :           course_code_csv['units'].values[0],
                        "timeslots" :       course_timeslot,
                        "class_days" :      course_class_days,
                        "offering_unit" :   tr[4].text,
                        "instructor_name" : instructor_name,
                        "venue" : course_venue,
                        "capacity": capacity,
                        "demand": demand,
                        "location" : location,
                    }
                )
    
    return courses

""" Couples lab sections to their corresponding lec sections """
def couple_lec_and_lab(lst):

    """ Checks if `x` is a sole lab section """
    def is_lab_section(x):
        return "lab" in list(x["class_days"].keys()) and "lec" not in list(x["class_days"].keys())

    """ Checks if `x` is a CS course """
    def is_cs_course(x):
        return x["course_code"].startswith("CS")

    # Only get 'CS' sections with lab
    sections_with_lab = list(filter(
        lambda x: is_lab_section(x) and is_cs_course(x),
        lst
    ))

    # Get 'CS' sections without lab
    sections_without_lab = list(filter(
        lambda x: not (is_lab_section(x) and is_cs_course(x)),
        lst
    ))

    # Container for lec sections to be removed later
    to_remove = []

    # Loop through the lab sections
    for course in sections_with_lab:
        # Get the lec section
        # -- Format: <course code> <lec section>/<lab section>
        code = course["course_code"]
        section = course["section_name"]["lab"].split('/')[0]

        # Check if lec section was previously found
        lec_section = list(filter(
            lambda x: f"{x['course_code']} {x['section_name']['lec']}" == f"{code} {section}",
            to_remove
        ))[:]   # returns [] if none was found;
                # otherwise, returns singleton

        if lec_section:
            lec_section = lec_section[0]
        else:
            # Lec section was not previously found yet
            # -- Check main set of lec sections
            lec_section = list(filter(
                lambda x: f"{x['course_code']} {x['section_name']['lec']}" == f"{code} {section}" and not is_lab_section(x),
                sections_without_lab
            ))[:]   # returns [] if none was found;
                    # otherwise, returns singleton

            if lec_section:
                lec_section = lec_section[0]
            else:
                # Lab section is standalone
                continue
        
        # Obtain lecture fields from `lec_section`
        course["section_name"]["lec"] = lec_section["section_name"]["lec"]
        course["class_days"]["lec"] = lec_section["class_days"]["lec"]
        course["instructor_name"]["lec"] = lec_section["instructor_name"]["lec"]
        course_class_days = course["class_days"]["lec"]
        course["timeslots"][course_class_days] = lec_section["timeslots"][course_class_days]

        # Check if it's the first time that `lec_section` was found
        if lec_section not in to_remove:
            to_remove.append(lec_section)

    # Remove lec sections in `to_remove`
    # -- these courses are not standalone
    for course in to_remove:
        lst.remove(course)

    return lst

""" Prints a dictionary """
def print_dict(d):
    print("--")
    for key,value in d.items():
        print(f"+ {key} : {value}")

# *Every new sem, just update start_year and end_year for app updates (?)
if __name__ == "__main__":
    """ course_list = get_courses()
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
    course_list_with_units.to_csv("csv/courses.csv", index=False) """
    for x in get_all_sections('cs 20'):
        print_dict(x)
    # query = "cs 10"
    # result = get_all_sections(query)
    # print("####\nbefore coupling:\n####")
    # for x in result:
    #     print_dict(x)
    # coupled_result = couple_lec_and_lab(result)
    # print("####\nafter coupling:\n####")
    # for x in coupled_result:
    #     print_dict(x)