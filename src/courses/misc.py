import numpy as np
#from schedule import Course

""" Obtain list of course codes """
def get_unique_courses(lst):
    done_course_codes = []
    unique_courses = []

    for course in lst:
        if course['course_code'] not in done_course_codes:
            unique_courses.append(course)
            done_course_codes.append(course['course_code'])

    return unique_courses

""" Unwrap value from dictionary """
def get_start_and_end(timeslot, day):
    for key, value in timeslot.items():
        if day in key:
            return timeslot[key]

def get_class_type_from_day(class_days, day):
    for key, value in class_days.items():
        if day in value:
            print(day,  key)
            return key

""" Obtain range of intervals given `start` and `end` """
# Example: start = 0, end = 60
# -- [15, 30, 45]
def get_ranges(start, end):
    return list(range(start+15, end, 15))

def has_class_in_day(class_days, day):
    return day in ''.join(list(class_days.values()))

""" Check if set of courses conflict with each other """
def is_conflicting(courses):
    for day in "MTWHFS":
        # 19 hours, 4 offsets per hour, 1 for end
        # -- 07:00 AM to 12:00 AM
        mat = np.zeros(19*4+1)

        ##print(courses)

        # Only obtain courses in DCP that have a class in `day`
        courses_with_classes = list(
            filter(
                lambda x: day in ''.join(list(x['class_days'].values())),
                courses
            )
        )

        # print(courses_with_classes)

        # Check if there are more than 2 classes
        # -- 0 or 1 class is trivially non-conflicting
        if len(courses_with_classes) > 1:

            # Get intervals of all the filtered courses
            slot_ranges: list[list[int]] = [
                get_ranges(*c['timeslots'].get(
                    get_class_type_from_day(c['class_days'],day)
                )) 
                for c in courses_with_classes
            ]

            # Loop through the ranges of each course
            for slot in slot_ranges:
                
                # Loop through each offset in the intervals
                for offset in slot:
                    # Get the index of the offset
                    # -- its position in the index
                    idx = offset // 15

                    # There's already a class that occupies the index
                    # -- conflicting!
                    if mat[idx] == 1:
                        return True

                    # Occupy the index
                    mat[idx] = 1             
    return False

""" Check if course to be added conflicts with the courses in DCP """
def is_conflicting_with_dcp(course, dcp_courses):
    courses = [course] + dcp_courses
    for day in "MTWHFS":
        print(day)
        # Check if course has a class on `day`
        if day in ''.join(list(course['timeslots'].keys())):
            # Only get DCP classes with a class on `day`
            dcp_with_classes = list(
                filter(
                    lambda x: day in ''.join(list(x['timeslots'].keys())), 
                    dcp_courses
                )
            )

            # Get range of intervals for the courses in DCP
            dcp_slot_ranges = [set(
                get_ranges(*get_start_and_end(
                    timeslot = c['timeslots'],
                    day = day
                ))
            ) for c in dcp_with_classes]
            
            # Get range of intervals for the course to be added in DCP
            course_range = set(
                get_ranges(*get_start_and_end(
                timeslot = course['timeslots'],
                day = day
            )))
            
            # DEBUGGING
            print(course['course_code'], course_range)
            print(*dcp_slot_ranges)
            if True in [course_range.intersection(slot_range) != set() for slot_range in dcp_slot_ranges]:
                return True
    
    return False

if __name__ == '__main__':
    #################
    ## FOR TESTING ##
    #################
    course = {
        "course_code": "CS 153",
        "course_title": "Introduction to Computer Security",
        "units": 3.0,
        "timeslot": {"TH": [180, 270]},
        "offeringunit": "DCS",
    }
    
    cs180 = Course(
        course_code="CS 180",
        section_name={"lec":"THR"},
        capacity=30,
        demand=30,
        units=3.0,
        class_days={"lec":"TH"},
        location={"lec":"AECH"}, venue={"lec":"SOLAIR"},
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
        location={"lec":"Accenture","lab":"TL2"}, venue={"lec":"Accenture", "lab":"TL2"},
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
        location={"lec":"AECH", "lab":"AECH"}, venue={"lec":"SOLAIR"},
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
        location={"lec":"SOLAIR"}, venue={"lec":"SOLAIR"},
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
        class_days={"lec":"WF"},
        location={"lec":"AECH"}, venue={"lec":"SOLAIR"},
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
        location={"lec":"AECH"}, venue={"lec":"SOLAIR"},
        # coords={"lec":(0,0)},
        instructor_name={"lec":"PAUL REGONIA"},
        timeslots={"lec":(360,450)},
        offering_unit="DCS"
    )

    dcp_courses = [cs180, cs145, cs153, cs132, cs192, lis51]
    dcp_courses = [x.__dict__ for x in dcp_courses]
    # print(dcp_courses)
    print(is_conflicting(dcp_courses))

