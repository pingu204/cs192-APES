from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import StrEnum, auto

""" Prints a dictionary """
def print_dict(d):
    print("--")
    for key,value in d.items():
        print(f"+ {key} : {value}")

""" Class for an instance of a course section """
@dataclass(frozen=True)
class Course:
    course_code:        str
    capacity:           int
    demand:             int
    units:              float
    section_name:       dict[str,str]
    class_days:         dict[str,str] 
                        # -- possible days: MTWHFS (H -> Thursday)
    location:           dict[str,str]
                        # -- for distance computation
    # coords:             dict[str, tuple[float,float]]
    instructor_name:    dict[str,str]
    timeslots:          dict[str, tuple[int,int]]
                        # -- value is `minute` offsets from 07:00 AM
    offering_unit:      str
    venue:              str

    @classmethod
    def from_dict(cls, d:dict):
        return cls(
            course_code = d.get('course_code'),
            course_title = d.get('course_title'),
            section_name = d.get('section_name'),
            units = d.get('units'),
            timeslots = d.get('timeslots'),
            class_days = d.get('class_days'),
            offering_unit = d.get('offering_unit'),
            instructor_name = d.get('instructor_name'),
            venue = d.get('venue'),
            capacity = d.get('capacity'),
            demand = d.get('demand'),
            location = d.get('location'),
        )

    @classmethod
    def example(self):
        return Course(
            course_code = "CS 192",
            section_name= {
                "lec":"TDE2/HUV2", 
                "lab":"TDE2/HUV2"
            },
            capacity = 30,
            demand = 30,
            units = 3.0,
            class_days = {
                "lec" : "TH",
            },
            location = {
                "lec" : "AECH",
            },
            # coords = {
            #     "lec" : (0,0),
            # },
            instructor_name = {
                "lec":"ROWENA SOLAMO",
            },
            timeslots = {
                "lec" : (90,180),
            },
            offering_unit = "DCS",
        )

class ClassStatus(StrEnum):
    STARTS_AT = auto()
    ONGOING = auto()

""" Obtains list of class days of a *saved* schedule """
def get_class_days_from_saved(sched):
    class_days: list[str] = []
    for course in sched.courses.all():
        class_days.extend(list(''.join(course.course_details['class_days'].values())))

    return list(set(class_days))

""" Obtains list of class days of a schedule """
def get_class_days(sched):
    class_days: list[str] = []
    for course in sched['courses']:
        class_days.extend(list(''.join(course['class_days'].values())))

    return list(set(class_days))
    


""" Return time in HH:MM AM/PM format """
def get_time(offset:int, extended:bool=True) -> str:
    # Base Time = 7:00 AM (year, month, and day are placeholders)
    dt = datetime(year=2000, month=1, day=1, hour=7) + timedelta(minutes=offset)

    # Shorten time string if not `extended`
    return dt.strftime("%I:%M %p") if extended else dt.strftime("%I %p")

""" Find class at day and current time """
def find_class(classes: list[Course], day:str, t:int) -> tuple[str, ClassStatus, int, int] | None:
    # for c in classes:
        # print_dict(c.__dict__)

    # Loop through the classes
    for i, c in enumerate(classes):
        
        # For each class, loop through each class type (lec/lab)
        for classType, (start,end) in c.timeslots.items():
            # print(c.course_code, classType)
            # Check if lec/lab section has a class on `day`
            if day not in c.class_days[classType]:
                continue
            
            # Check if class starts at `t`
            if start == t:
                course_code = f"{c.course_code} "
                match classType:
                    case "lec":
                        course_code += c.section_name[classType]
                    case "lab":
                        course_code += f"{'lab ' + c.section_name[classType]}"
                # course_code = f"{c.course_code} {"lab " + c.section_name[classType] if classType == "lab" else c.section_name[classType]}"
                timeslot = f"{get_time(offset=start)} - {get_time(offset=end)}"
                location = c.venue.get(classType, "Unknown Location") # edited since KeyError raised (e.g., CS 194) 

                return f"<b>{course_code}</b><br>{timeslot}<br>{location}", ClassStatus.STARTS_AT, end-start, i

            elif start < t < end:
                return c.course_code, ClassStatus.ONGOING, end-start, i

    return None # No class at `day` and `time`

""" Returns the contents of the HTML timetable given list of `classes` """
def generate_timetable(classes:list[Course], glow_idx:int=-1):
    
    # Header for days
    # -- Shortened days for export ver.
    main_days_header = '<tr class="days-header"><th></th><th>MONDAY</th><th>TUESDAY</th><th>WEDNESDAY</th><th>THURSDAY</th><th>FRIDAY</th><th>SATURDAY</th></tr>'
    export_days_header = '<tr class="days-header"><th></th><th>MON</th><th>TUES</th><th>WED</th><th>THURS</th><th>FRI</th><th>SAT</th></tr>'

    # Header for last boundary
    main_last_header = '<tr class="bound"><th>12:00 AM</th><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
    export_last_header = '<tr class="bound"><th>12 AM</th><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
    
    # Container for output
    main_output =   []
    export_output = []

    # Markers
    start, end = 5000, -1

    # Loop through each offset 
    # -- Note: Each offset represents one row in the table
    # -- 07:00 AM to 12:00 AM
    for i in range(17*4): # 17 hours, 4 offset per hour

        # Base string for the row
        main_row_str:str =   ""
        export_row_str:str = ""
        
        # Display time at whole hour
        # -- e.g. i = 60 => 8:00 AM

        # -- Get the residual minute, then check if current time is a boundary
        minute:int = ((i*15)%60)
        is_bound:bool = minute == 0

        # -- Configure row header based on `is_bound`
        main_row_str += f"<th>{get_time(offset=i*15)}</th>" if is_bound else "<th></th>" 
        export_row_str += f"<th>{get_time(offset=i*15, extended=False)}</th>" if is_bound else "<th></th>"

        # Loop through each day
        # -- Note: Each day represents one column
        for day in ['M','T','W','H','F','S']:

            # Check if a class exists at current day and time
            current_class = find_class(classes, day, i*15)

            if current_class:
                # Update `start` if first class was found
                start = min(start, i)

                # Update `end` each time a class is found
                end = max(end, i)

                # Decompose `current_class`; check type annotation of find_class()
                c_str, status, length, idx = current_class

                # Configure row spanning at the boundary
                # -- Note: if `status` == ONGOING, the `td` is skipped because of row spanning
                if status == ClassStatus.STARTS_AT:
                    if glow_idx != -1:
                        if glow_idx == idx: 
                            main_row_str += f'<td rowspan="{length/15}"><div id="td-{idx+1}" class="rowspanned glow">{c_str}</div></td>'
                        else:
                            main_row_str += f'<td rowspan="{length/15}"><div class="rowspanned">{c_str}</div></td>'
                    else:
                        main_row_str += f'<td rowspan="{length/15}"><div id="td-{idx+1}" class="rowspanned">{c_str}</div></td>'
                    export_row_str += f'<td rowspan="{length/15}"><div id="td-{idx+1}" class="rowspanned">{c_str}</div></td>'

            else: # No class in time cell
                main_row_str += f'<td></td>'
                export_row_str += f'<td></td>'
        
        # Append row string to the output container
        main_output.append(f"<tr>{main_row_str}</tr>" if not is_bound else f'<tr class="bound">{main_row_str}</tr>')
        export_output.append(f"<tr>{export_row_str}</tr>" if not is_bound else f'<tr class="bound">{export_row_str}</tr>')

    # Collate row strings
    main_output = [main_days_header] + (main_output + [main_last_header])[(start//4)*4:(end//4+1)*4+1]
    export_output = [export_days_header] + (export_output + [export_last_header])[(start//4)*4:(end//4+1)*4+1]

    return '\n'.join(main_output), '\n'.join(export_output)

# print('\n'.join(main_output))

"""
if __name__ == '__main__':

    print(Course.example())

    cs180 = Course(
        course_code="CS 180",
        section_name={"lec":"THR"},
        capacity=30,
        demand=30,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"ROSELYN GABUD"},
        timeslots={"lec":(600,780)},
        offering_unit="DCS"
    )

    cs145 = Course(
        course_code="CS 145",
        section_name={"lec":"HONOR", "lab":"HONOR 2"},
        capacity=30,
        demand=1,
        units=4.0,
        class_days={"lec":"TH","lab":"M"},
        location={"lec":"Accenture","lab":"TL2"},
        # coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"WILSON TAN", "lab":"GINO SAMPEDRO"},
        timeslots={"lec":(450,540), "lab":(240,420)},
        offering_unit="DCS"
    )

    cs192 = Course(
        course_code="CS 192",
        section_name={"lec":"TDE2/HUV2", "lab":"TDE2/HUV2"},
        capacity=30,
        demand=1,
        units=3.0,
        class_days={"lec":"T", "lab":"H"},
        location={"lec":"AECH", "lab":"AECH"},
        # coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"ROWENA SOLAMO", "lab":"ROWENA SOLAMO"},
        timeslots={"lec":(180,300), "lab":(180,360)},
        offering_unit="DCS"
    )

    lis51 = Course(
        course_code="LIS 51",
        section_name={"lec":"WFU"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"SOLAIR"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"DRIDGE REYES"},
        timeslots={"lec":(90,270)},
        offering_unit="SLIS"
    )

    cs153 = Course(
        course_code="CS 153",
        section_name={"lec":"THW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"PHILIP ZUNIGA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    cs132 = Course(
        course_code="CS 132",
        section_name={"lec":"WFW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"AECH"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"PAUL REGONIA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    classes = [cs180, cs145, cs153, cs132, cs192, lis51]

    main_table, export_table = generate_timetable(classes)

    print(main_table)

    print(export_table)
"""