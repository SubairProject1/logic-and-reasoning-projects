from pandas import DataFrame

###################################################################################################
#                                  Checker and pretty printer                                     #
###################################################################################################
def check_schedule(schedule: DataFrame,
                   days: list[str],
                   courses: list[str],
                   rooms: DataFrame,
                   students_courses: DataFrame):
    '''
    Check if the schedule is valid
    Returns True if the schedule is valid, False otherwise

    input:
    - schedule: a DataFrame with columns 'Course', 'Day', and 'Room'

    '''
    # check that each course is scheduled only once
    scheduled = set()
    for course in schedule["Course"]:
        if course in scheduled:
            print("The course", course, "is scheduled more than once.")
            return False
        scheduled.add(course)
    # check that every course is scheduled
    if scheduled != set(courses):
        print("Some courses are not scheduled.")
        return False

    # check that no extra day is used
    for day in schedule['Day']:
        if day not in days:
            print("The day", day, "is not in the list of days.")
            return False

    # check that each (room, day) is used only once
    scheduled = set()
    for room, day in schedule[['Room', 'Day']].values:
        if (room, day) in scheduled:
            print("The room", room, "is used more than once on day.", day)
            return False
        scheduled.add((room, day))

    # check that no student has two exams at the same time
    for student, course_set in students_courses[['Student', 'Courses']].values:
        busy_days = set()
        for course in course_set:
            for day in schedule[schedule['Course'] == course]['Day']:
                if day in busy_days:
                    print("The student", student, "has two exams on the same day.")
                    return False
                busy_days.add(day)

    # check that the capacity of the room is not exceeded
    for course, room in schedule[['Course', 'Room']].values:
        if students_courses[students_courses['Courses'].apply(lambda x: course in x)]['Student'].count() > rooms[rooms['Room'] == room]['Capacity'].values[0]:
            print("The capacity of the room", room, "is exceeded.")
            return False
    return True

def print_schedule(schedule: DataFrame,
                   days : list[str],
                   courses : list[str],
                   rooms : DataFrame):
    '''
    Prints the schedule in a nice week view
    '''
    schedule.set_index(['Room', 'Day'], inplace=True)
    longest_course_name = max([len(course) for course in courses])
    longest_day_name = max([len(day) for day in days])
    longest_room_name = max([len(str(room)) for room in rooms['Room']])

    longest_horizontal = max(longest_course_name, longest_day_name)

    # split the schedule into weeks of 5 time_slots
    weeks = []
    for i in range(0, len(days), 5):
        weeks.append(days[i:i+5])
    for week in weeks:
        print(' ' * longest_room_name, end=' | ')
        for day in week:
            day = day + ' ' * ((longest_horizontal - len(day)) // 2)
            day =  ' ' * (longest_horizontal - len(day)) + day
            print(day, end=' | ')
        print('')
        print('-' * (longest_room_name + 3 + len(week) * (longest_horizontal + 3)))


        for room in rooms['Room']:
            room_name = str(room)
            # pad the room name
            room_name = room_name + ' ' * (longest_room_name - len(room_name))
            room_name = ' ' * (longest_room_name - len(room_name)) + room_name
            print(room_name, end=' | ')
            for day in week:
                if (room, day) in schedule.index:
                    course = schedule.loc[(room, day), 'Course']
                    # pad the course name
                    course = course + ' ' * ((longest_horizontal - len(course)) // 2)
                    course = ' ' * (longest_horizontal - len(course)) + course
                    print(course, end=' | ')
                else:
                    print(' ' * (longest_horizontal), end=' | ')
            print('')
            print('-' * (longest_room_name + 3 + len(week) * (longest_horizontal + 3)))
        print('')
    schedule.reset_index(inplace=True)
