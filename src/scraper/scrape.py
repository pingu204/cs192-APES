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
    
    for letter in list(string.ascii_lowercase):
        soup = parse_html(BASE_URL+letter, "tr")
        for row in soup[4:]:
            tr = row.find_all("td")

            # Check if there are no classes
            if (tr[0].text != "No courses to display"):
                courses.append(
                    {
                        "course_code" : tr[0].text,
                        "course_title" : tr[1].text,
                        "offering_unit" : tr[3].text,
                    }
                )
        print(f"+ '{letter.capitalize()}' courses DONE")
    
    return pd.DataFrame(courses)

""" Parses course code from `td` element """
def get_course_code(raw_code: str):
    # Only extract first line of the element in case of 
    # multi-line course codes
    # -- e.g.   Bioinfo 297 HQR<br/>Computational Phylogenetics
    # --        should be 'Bioinfo 297 HQR'
    # Remove section names
    # -- e.g.   Bioinfo 297 HQR should be 'Bioinfo 297'
    return (' '.join(raw_code.split('\n')[0].split(' ')[:-1])).rstrip()

""" Obtain units of all subjects in CRS from Acad. Years `start` to `end` """
def get_units(start:int , end:int):
    BASE_URL = "https://crs.upd.edu.ph/schedule/120"

    # Container for values
    units: dict[str, float] = {}

    # Load .csv files
    courses_csv =   pd.read_csv("courses.csv", sep='\t')
    units_csv =     pd.read_csv("units.csv", sep='\t')
    
    # Remove those that already have encoded units
    course_codes =  list(set(courses_csv["course_code"].tolist()) - set(units_csv["course_code"].tolist()))

    for year in range(end, start-1, -1): # A.Y 2018-2019 to A.Y. 2024-2025
        for sem in [1,2]:
            print(f"A.Y. {year}-{year+1}, Sem {sem}")
            
            for letter in list(set([word[0] for word in course_codes])):
                soup = parse_html(f"{BASE_URL}{year}{sem}/{letter}/", "tr")

                for row in soup[1:]:
                    tr = row.find_all("td")

                    # Check if there are no classes 
                    if (tr[0].text != "No classes to display"):
                        course_code = get_course_code(tr[1].get_text(separator='\n'))
                        
                        if course_code not in course_codes:
                            continue
                        else:
                            print(f"+ {course_code}")
                            units[course_code] = float(tr[2].text)
                            course_codes.remove(course_code)

            if course_codes == []:
                break

        if course_codes == []:
            break

        print(f"Remaining: {len(course_codes)}")

    return pd.DataFrame({"course_code" : list(units.keys()), "units" : list(units.values())})

courses_csv = pd.read_csv("courses.csv", sep='\t', index_col=0)
units_csv = pd.read_csv("units.csv", sep='\t', index_col=0)

print(courses_csv)
print(units_csv)

print(courses_csv.merge(units_csv, on="course_code", how="left"))

print(get_courses())
