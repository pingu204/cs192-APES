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
def get_units(start_year:int, end_year:int, course_codes:list[str]):
    # Note: start_year must be <= end_year
    # -- e.g. start_year = 2016, end_year = 2022 scrapes data from A.Y. 2016-2017 to A.Y. 2022-2023
    BASE_URL = "https://crs.upd.edu.ph/schedule/120"

    # Container for values
    units: dict[str, float] = {}
    len_courses = len(course_codes)

    # Get the last two digits of the years
    start_year %= 100
    end_year %= 100

    for year in range(end_year, start_year-1, -1):
        for sem in [1, 2, 4]: # Semester Number (4 = Midyear)
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
                            course_codes.remove(course_code)

            if course_codes == []:
                break

        if course_codes == []:
            break

        
    print(f"\n[Found: {len_courses - len(course_codes)}/{len_courses}]")

    return pd.DataFrame({
        "course_code" : list(units.keys()), 
        "units" :       list(units.values()),
    })

if __name__ == "__main__":
    course_list = get_courses()
    print(course_list)

    units_list = get_units(
        start_year =    2024,
        end_year =      2024, 
        course_codes =  list(set(course_list["course_code"].tolist()))[:10],
    )
    print(units_list)

    course_list_with_units = course_list.merge(units_list, on="course_code", how="left")
    print(course_list_with_units)

    course_list_with_units.to_csv("csv/courses.csv", index=False)

