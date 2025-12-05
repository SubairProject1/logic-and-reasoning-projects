from pandas import DataFrame
from itertools import combinations

# Using global mapping to store the correspondence between variable numbers and (course, day, room) triples.
global_var_mapping = {}

###################################################################################################
#                                      Helper functions                                           #
###################################################################################################

# None

###################################################################################################
#                                      Main functions                                             #
###################################################################################################
'''
Encoding:
Each variable represents the assignment of a course to a specific (day, room) pair — 
meaning the course is scheduled on that day and in that room.

The CNF formula is built with the following constraints:
1. Each course is scheduled **exactly once**, i.e., in exactly one room and on exactly one day.
   - This single constraint ensures both:
     a) each course is assigned to one day,
     b) and each course is assigned to one room.
2. No two exams occur in the same room on the same day.
3. No student has two exams scheduled on the same day.

How this is done:
- Variables are created for valid (course, day, room) combinations, considering room capacity.
- A global mapping stores which (course, day, room) each variable refers to.
- For each course, we ensure exactly one such variable is true (others false).
- Room/day collisions and student schedule conflicts are resolved by adding pairwise exclusion clauses.
'''
def encode_cnf(days: list[str],
               courses: list[str],
               rooms: DataFrame,
               students_courses: DataFrame):
    '''
    Encode the exam scheduling problem as a CNF formula.
    
    input:
    - days: list of available exam days
    - courses: list of course names
    - rooms: DataFrame with columns 'Room' and 'Capacity'
    - students_courses: DataFrame with columns 'Student' and 'Courses' (a list of enrolled courses)
    
    output:
    - cnf: list of clauses, where each clause is a list of integer literals
    '''
    cnf: list[list[int]] = []
    ### YOUR CODE HERE ###
    
    global global_var_mapping
    global_var_mapping = {}  # Maps variable numbers to (course, day, room)
    var_num = 1

    # Count how many students are enrolled in each course
    enrollment = {course: 0 for course in courses}
    for _, row in students_courses.iterrows():
        for course in row['Courses']:
            if course in enrollment:
                enrollment[course] += 1

    # Create variables for valid (course, day, room) combinations, considering room capacity
    allowed_vars_by_course = {course: [] for course in courses}
    allowed_vars_by_course_day = {}
    allowed_vars_by_day_room = {}

    for course in courses:
        for day in days:
            for _, room_row in rooms.iterrows():
                room = room_row['Room']
                capacity = room_row['Capacity']
                if capacity >= enrollment[course]:
                    global_var_mapping[var_num] = (course, day, room)
                    allowed_vars_by_course[course].append(var_num)
                    allowed_vars_by_course_day.setdefault((course, day), []).append(var_num)
                    allowed_vars_by_day_room.setdefault((day, room), []).append(var_num)
                    var_num += 1

    # Constraint 1: Each course is scheduled exactly once (covers both day and room)
    for course, vars_list in allowed_vars_by_course.items():
        if vars_list:
            cnf.append(vars_list.copy())  # At least one valid assignment
        for v1, v2 in combinations(vars_list, 2):  # At most one
            cnf.append([-v1, -v2])

    # Constraint 2: No two courses in the same room on the same day
    for (day, room), vars_list in allowed_vars_by_day_room.items():
        for v1, v2 in combinations(vars_list, 2):
            cnf.append([-v1, -v2])

    # Constraint 3: No student has two exams on the same day
    # (This is the fourth constraint)
    for _, row in students_courses.iterrows():
        student_courses = row['Courses']
        for c1, c2 in combinations(student_courses, 2):
            for day in days:
                vars_c1 = allowed_vars_by_course_day.get((c1, day), [])
                vars_c2 = allowed_vars_by_course_day.get((c2, day), [])
                for v1 in vars_c1:
                    for v2 in vars_c2:
                        cnf.append([-v1, -v2])
    
    return cnf

def decode_model(model: list[int],
                 days: list[str],
                 courses: list[str],
                 rooms: DataFrame,
                 students_course: DataFrame):
    '''
    Given a model, returns the schedule as a DataFrame
    The schedule is a DataFrame with columns 'Course', 'Day', and 'Room'
    
    input:
    - model: the model returned by the SAT solver
        The model is a list of literals
        Literals are positive or negative integers representing respectively a variable or its negation.
    - days: a list of days to schedule the exams
    - rooms: a DataFrame with columns 'Room' and 'Capacity'
    - course_list: a list of courses
    - students_course: a DataFrame with columns 'Student' and 'Courses'
    
    Note:
    It is possible that not all inputs are used in the function.
    
    output:
    - schedule: a DataFrame with columns 'Course', 'Day', and 'Room'
    '''
    schedule = DataFrame(columns=['Course', 'Day', 'Room'])
    ### YOUR CODE HERE ###

    global global_var_mapping
    schedule_entries = []

    # Process only positive literals
    for literal in model:
        if literal > 0 and literal in global_var_mapping:
            course, day, room = global_var_mapping[literal]
            schedule_entries.append({'Course': course, 'Day': day, 'Room': room})
    
    schedule = DataFrame(schedule_entries, columns=['Course', 'Day', 'Room'])

    return schedule