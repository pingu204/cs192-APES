from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import StrEnum, auto
""" Class for an instance of a course section """
@dataclass(frozen=True)
class Course:
    course_code:        str
    capacity:           int
    demand:             int
    units:              float
    sectionName:        dict[str,str]
    class_days:         dict[str,str] 
                        # -- possible days: MTWHFS (H -> Thursday)
    location:           dict[str,str]
    coords:             dict[str, tuple[float,float]]
    instructor_name:    dict[str,str]
    timeslots:          dict[str, tuple[int,int]]
                        # -- value is `minute` offsets from 07:00 AM
    offering_unit:      str

    @classmethod
    def example(self):
        return Course(
            course_code = "CS 192",
            sectionName= {
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
            coords = {
                "lec" : (0,0),
            },
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

""" Return time in HH:MM AM/PM format """
def get_time(offset:int) -> str:
    # Base Time = 7:00 AM (year, month, and day are placeholders)
    dt = datetime(year=2000, month=1, day=1, hour=7) + timedelta(minutes=offset)
    return dt.strftime("%I:%M %p")

""" Find class at day and current time """
def find_class(classes: list[Course], day:str, t:int) -> tuple[str, ClassStatus, int, int] | None:
    # Loop through the classes
    for i, c in enumerate(classes):
        
        # For each class, loop through each class type (lec/lab)
        for classType,(start,end) in c.timeslots.items():
            
            # Check if lec/lab section has a class on `day`
            if day not in c.class_days[classType]:
                continue
            
            # Check if class starts at `t`
            if start == t:
                course_code = f"{c.course_code} "
                match c.sectionName[classType]:
                    case "lec":
                        course_code += c.sectionName[classType]
                    case "lab":
                        course_code += f"{'lab ' + c.sectionName[classType]}"
                # course_code = f"{c.course_code} {"lab " + c.sectionName[classType] if classType == "lab" else c.sectionName[classType]}"
                timeslot = f"{get_time(offset=start)} - {get_time(offset=end)}"
                location = c.location[classType]

                return f"<b>{course_code}</b><br>{timeslot}<br>{location}", ClassStatus.STARTS_AT, end-start, i

            elif start < t < end:
                return c.course_code, ClassStatus.ONGOING, end-start, i

    return None # No class at `day` and `time`

""" Returns the contents of the HTML timetable given list of `classes` """
def generate_timetable(classes: list[Course]):
    # Container for output
    to_print = ["<tr><th></th><th>MONDAY</th><th>TUESDAY</th><th>WEDNESDAY</th><th>THURSDAY</th><th>FRIDAY</th><th>SATURDAY</th></tr>"]

    # Loop through each offset 
    # -- Note: Each offset represents one row in the table
    for i in range(48):

        # Base string for the row
        row_str:str = ""
        
        # Display time at whole hour
        # -- e.g. i = 60 => 8:00 AM

        # -- Get the residual minute, then check if current time is a boundary
        minute:int = ((i*15)%60)
        is_bound:bool = minute == 0

        # -- Configure row header based on `is_bound`
        row_str += f"<th>{get_time(offset=i*15)}</th>" if is_bound else "<th></th>" 

        # Loop through each day
        # -- Note: Each day represents one column
        for day in ['M','T','W','H','F','S']:

            # Check if a class exists at current day and time
            current_class = find_class(classes, day, i*15)

            if current_class:
                # Decompose `current_class`; check type annotation of find_class()
                c_str, status, length, idx = current_class

                # Configure row spanning at the boundary
                # -- Note: if `status` == ONGOING, the `td` is skipped because of row spanning
                if status == ClassStatus.STARTS_AT:
                    row_str += f'<td id="td-{i+1}" class="rowspanned" rowspan="{length/15}">{c_str}</td>'

            else: # No class in time cell
                row_str += f'<td></td>'
        
        # Append row string to the output container
        to_print.append(f"<tr>{row_str}</tr>" if not is_bound else f'<tr class="bound">{row_str}</tr>')

    # Add row for 07:00 PM
    to_print.append('<tr class="bound"><th>07:00 PM</th><td></td><td></td><td></td><td></td><td></td><td></td></tr>')

    return to_print

# print('\n'.join(to_print))

if __name__ == '__main__':

    print(Course.example())

    cs180 = Course(
        course_code="CS 180",
        sectionName={"lec":"THR"},
        capacity=30,
        demand=30,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"},
        coords={"lec":(0,0)},
        instructor_name={"lec":"ROSELYN GABUD"},
        timeslots={"lec":(90,180)},
        offering_unit="DCS"
    )

    cs145 = Course(
        course_code="CS 145",
        sectionName={"lec":"HONOR", "lab":"HONOR 2"},
        capacity=30,
        demand=1,
        units=4.0,
        class_days={"lec":"TH","lab":"M"},
        location={"lec":"Accenture","lab":"TL2"},
        coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"WILSON TAN", "lab":"GINO SAMPEDRO"},
        timeslots={"lec":(450,540), "lab":(240,420)},
        offering_unit="DCS"
    )

    cs192 = Course(
        course_code="CS 192",
        sectionName={"lec":"TDE2/HUV2", "lab":"TDE2/HUV2"},
        capacity=30,
        demand=1,
        units=3.0,
        class_days={"lec":"T", "lab":"H"},
        location={"lec":"AECH", "lab":"AECH"},
        coords={"lec":(0,0), "lab":(0,0)},
        instructor_name={"lec":"ROWENA SOLAMO", "lab":"ROWENA SOLAMO"},
        timeslots={"lec":(180,300), "lab":(180,360)},
        offering_unit="DCS"
    )

    lis51 = Course(
        course_code="LIS 51",
        sectionName={"lec":"WFU"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"SOLAIR"},
        coords={"lec":(0,0)},
        instructor_name={"lec":"DRIDGE REYES"},
        timeslots={"lec":(180,270)},
        offering_unit="SLIS"
    )

    cs153 = Course(
        course_code="CS 153",
        sectionName={"lec":"THW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"},
        coords={"lec":(0,0)},
        instructor_name={"lec":"PHILIP ZUNIGA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    cs132 = Course(
        course_code="CS 132",
        sectionName={"lec":"WFW"},
        capacity=30, demand=1,
        units=3.0,
        class_days={"lec":"WF"},
        location={"lec":"AECH"},
        coords={"lec":(0,0)},
        instructor_name={"lec":"PAUL REGONIA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    classes = [cs180, cs145, cs153, cs132, cs192, lis51]

    print(generate_timetable(classes))