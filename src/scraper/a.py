from scrape import *
import pandas as pd
import unittest

""" For testing lang! """

# print(get_all_sections("Physics 71"))
""" print("7-8:15AM", convert_time("7-8:15AM"))
print("2:30-4PM", convert_time("2:30-4PM"))
print("10AM-1PM", convert_time("10AM-1PM")) """
""" #print(get_info_from_csv("CS 11"))
result = get_info_from_csv("CS 11")
print(result['course_code'].values[0]) """

""" test_str = [
    'App Physics 181 WFY-FX-1',
    'CS 145 EXCELLENCE 2',
    'Physics 71 THQ-FQ-1',
    'TM 271 271 A'
]

for s in test_str:
    print("{0:30} {1}".format(s, get_course_code(s))) """

COURSE_CODE_CSV = pd.read_csv("csv/courses.csv", sep=",")

COURSE_CODE_LIST: list[str] = COURSE_CODE_CSV["course_code"].tolist()


class TestCourseCodeExtractor(unittest.TestCase):
    def test_get_course_code(self):
        for code in COURSE_CODE_LIST:
            self.assertEqual(
                get_course_code(code + " DUMMY_SECTION"), code, f"Error for {code}"
            )


if __name__ == "__main__":
    unittest.main()
