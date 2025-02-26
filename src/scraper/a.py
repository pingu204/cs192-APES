from scrape import *

""" For testing lang! """

#print(get_all_sections("Physics 71"))
""" print("7-8:15AM", convert_time("7-8:15AM"))
print("2:30-4PM", convert_time("2:30-4PM"))
print("10AM-1PM", convert_time("10AM-1PM")) """
#print(get_info_from_csv("CS 11"))
result = get_info_from_csv("CS 11")
print(result['course_code'].values[0])