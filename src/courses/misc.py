import numpy as np

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

""" Obtain range of intervals given `start` and `end` """
# Example: start = 0, end = 60
# -- [15, 30, 45]
def get_ranges(start, end):
    return list(range(start+15, end, 15))

""" Check if set of courses conflict with each other """
def is_conflicting(courses):
    for day in "MTWHFS":
        # 12 hours, 4 offsets per hour, 1 for end
        mat = np.zeros(12*4+1)

        courses_with_classes = list(
            filter(
                lambda x: day in ''.join(list(x['timeslot'].keys())), 
                courses
            )
        )

        if len(courses_with_classes) > 1:
            slot_ranges: list[list[int]] = [
                get_ranges(*get_start_and_end(
                    timeslot = c['timeslot'],
                    day = day
                )) for c in courses_with_classes]

            for slot in slot_ranges:
                for offset in slot:
                    idx = offset // 15
                    if mat[idx] == 1:
                        return True
                    mat[idx] = 1
        
    return False

""" Check if course to be added conflicts with the courses in DCP """
def is_conflicting_with_dcp(course, dcp_courses):
    courses = [course] + dcp_courses
    for day in "MTWHFS":
        print(day)
        # Check if course has a class on `day`
        if day in ''.join(list(course['timeslot'].keys())):
            # Only get DCP classes with a class on `day`
            dcp_with_classes = list(
                filter(
                    lambda x: day in ''.join(list(x['timeslot'].keys())), 
                    dcp_courses
                )
            )

            # Get range of intervals for the courses in DCP
            dcp_slot_ranges = [set(
                get_ranges(*get_start_and_end(
                    timeslot = c['timeslot'],
                    day = day
                ))
            ) for c in dcp_with_classes]
            
            # Get range of intervals for the course to be added in DCP
            course_range = set(
                get_ranges(*get_start_and_end(
                timeslot = course['timeslot'],
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
    

    dcp_courses = [
        {
            "course_code": "CS 145",
            "course_title": "Computer Networks",
            "units": 4.0,
            "timeslot": {"TH": [540, 630]},
            "offeringunit": "DCS",
        }, {
            "course_code": "CS 192",
            "course_title": "Software Engineering II",
            "units": 3.0,
            "timeslot": {"H": [0, 180], "T": [60, 180]},
            "offeringunit": "DCS",
        }, {
            "course_code": "CS 132",
            "course_title": "Introduction to Data Science",
            "units": 3.0,
            "timeslot": {"WF": [270, 360]},
            "offeringunit": "DCS",
        }, {
            "course_code": "Eng 118",
            "course_title": "English Semantics",
            "units": 3.0,
            "timeslot": {"TH": [90, 180]},
            "offeringunit": "DECL",
        }

    ]

    print(is_conflicting(dcp_courses))

