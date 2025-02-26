def get_unique_courses(lst):
    done_course_codes = []
    unique_courses = []

    for course in lst:
        if course['course_code'] not in done_course_codes:
            unique_courses.append(course)
            done_course_codes.append(course['course_code'])

    return unique_courses

""" Unwraps value from dictionary """
def get_start_and_end(timeslot, day):
    for key, value in timeslot.items():
        if day in key:
            return timeslot[key]

""" Obtain range of intervals given `start` and `end` """
# Example: start = 0, end = 60
# -- [15, 30, 45]
def get_ranges(start, end):
    return list(range(start+15, end, 15))

""" Check if course to be added conflicts with the courses in DCP """
def is_conflicting_with_dcp(course, dcp_courses):
    courses = [course] + dcp_courses
    for day in "MTWHFS":
        # Check if the courses have a class on `day`
        if not (False in [
            day in ''.join(list(x['timeslot'].keys())) for x in courses
        ]):
            # Get range of intervals for the courses in DCP
            dcp_slot_ranges = [set(
                get_ranges(*get_start_and_end(
                    timeslot = c['timeslot'],
                    day = day
                ))
            ) for c in dcp_courses]
            
            # Get range of intervals for the course to be added in DCP
            course_range = set(
                get_ranges(*get_start_and_end(
                timeslot = course['timeslot'],
                day = day
            )))

            print(course_range, *dcp_slot_ranges)
            
            if False not in [course_range.intersection(x) == set() for x in dcp_slot_ranges]:
                return False
    
    return True

if __name__ == '__main__':

    course = {
        'timeslot':{
            'M':(0,60),
            'TTh':(60,120),
        }
    }

    dcp_courses = [
        {
            'timeslot':{
                'M':(0,360),
                'TTh':(120,180),
            }
        },
        {
            'timeslot':{
                'M':(480,540),
            }
        },
    ]

    print(is_conflicting_with_dcp(course, dcp_courses))

