"""
Data genration script
"""
import random
from datetime import datetime, timedelta
import mysql.connector
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

conn = mysql.connector.connect(host="localhost", user="uni_admin", password="uniadmin", database="university_portal")
cur = conn.cursor()

# 1. Departments 

base_dept_names = ["Computer Science", "Mathematics", "Physics", "Business Administration",
              "Electrical Engineering", "Biology", "Psychology", "Economics",
              "Civil Engineering", "English Literature", "Chemistry", "Sociology",
              "Political Science", "Mechanical Engineering", "History", "Philosophy",
              "Nursing", "Architecture", "Environmental Science", "Statistics"]

for name in base_dept_names[:20]:
    cur.execute(
        "INSERT INTO departments (department_name, building) VALUES (%s, %s)",
        (name, f"Building {random.choice(['A','B','C','D','E'])}{random.randint(1,9)}")
    )

conn.commit()
cur.execute("SELECT department_id FROM departments")
dept_ids = [r[0] for r in cur.fetchall()]

# 2. Programs 

degree_levels = ["Bachelor", "Master", "PhD"]
cur.execute("SELECT department_id, department_name FROM departments")
dept_name_map = {r[0]: r[1] for r in cur.fetchall()}
for dept_id in dept_ids:
    level = random.choice(degree_levels)
    duration = 4 if level == "Bachelor" else (2 if level == "Master" else 5)
    degree_label = {"Bachelor": "B.Sc.", "Master": "M.Sc.", "PhD": "Ph.D."}[level]
    pname = f"{degree_label} in {dept_name_map[dept_id]}"
    cur.execute(
        "INSERT INTO programs (program_name, department_id, degree_level, duration_years) VALUES (%s,%s,%s,%s)",
        (pname, dept_id, level, duration)
    )
conn.commit()
cur.execute("SELECT program_id FROM programs")
program_ids = [r[0] for r in cur.fetchall()]

# 3. Instructors 

for _ in range(40):
    first, last = fake.first_name(), fake.last_name()
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999999)}@university.edu"
    cur.execute(
        "INSERT INTO instructors (first_name, last_name, email, department_id, hire_date) VALUES (%s,%s,%s,%s,%s)",
        (first, last, email, random.choice(dept_ids), fake.date_between(start_date='-20y', end_date='-1y'))
    )
conn.commit()
cur.execute("SELECT instructor_id, department_id FROM instructors")
instructors = cur.fetchall()

# 4. Students 

statuses = ["Active", "Active", "Active", "Graduated", "Suspended", "Withdrawn"]
for _ in range(150):
    first, last = fake.first_name(), fake.last_name()
    email = f"{first.lower()}.{last.lower()}{random.randint(1,999999)}@student.university.edu"
    dob = fake.date_of_birth(minimum_age=18, maximum_age=30)
    enroll_date = fake.date_between(start_date='-4y', end_date='today')
    gpa = round(random.uniform(2.0, 4.0), 2)
    cur.execute(
        """INSERT INTO students (first_name, last_name, email, date_of_birth, enrollment_date, program_id, status, gpa)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (first, last, email, dob, enroll_date, random.choice(program_ids), random.choice(statuses), gpa)
    )
conn.commit()
cur.execute("SELECT student_id FROM students")
student_ids = [r[0] for r in cur.fetchall()]

# 5. User accounts (1 per student)

for sid in student_ids:
    username = f"stu{sid}_{fake.user_name()[:10]}"
    pw_hash = fake.sha256()
    last_login = fake.date_time_between(start_date='-60d', end_date='now')
    cur.execute(
        "INSERT INTO user_accounts (student_id, username, password_hash, role, last_login) VALUES (%s,%s,%s,%s,%s)",
        (sid, username, pw_hash, 'student', last_login)
    )
conn.commit()

# 6. Courses (60)[cite: 6]

subjects = ["Introduction to", "Advanced", "Principles of", "Applied", "Theory of",
            "Fundamentals of", "Topics in", "Seminar in"]
topics = ["Algorithms", "Databases", "Calculus", "Linear Algebra", "Quantum Mechanics",
          "Marketing", "Circuit Design", "Genetics", "Cognitive Psychology", "Macroeconomics",
          "Structural Engineering", "Shakespeare", "Machine Learning", "Operating Systems",
          "Statistics", "Thermodynamics", "Organizational Behavior", "Microbiology"]
used_codes = set()
for i in range(60):
    dept_id = random.choice(dept_ids)
    code = f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{random.randint(100,499)}"
    while code in used_codes:
        code = f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{random.randint(100,499)}"
    used_codes.add(code)
    name = f"{random.choice(subjects)} {random.choice(topics)}"
    credits = random.choice([3, 3, 3, 4, 1, 2])
    cur.execute(
        "INSERT INTO courses (course_code, course_name, credits, department_id) VALUES (%s,%s,%s,%s)",
        (code, name, credits, dept_id)
    )
conn.commit()
cur.execute("SELECT course_id, department_id FROM courses")
courses = cur.fetchall()

# 7. Course offerings 

terms = [("Fall", 2024), ("Spring", 2025), ("Fall", 2025), ("Spring", 2026)]
offering_ids = []
seen_offerings = set()
while len(offering_ids) < 110:
    course_id, dept_id = random.choice(courses)
    matching_instructors = [i[0] for i in instructors if i[1] == dept_id] or [i[0] for i in instructors]
    instructor_id = random.choice(matching_instructors)
    semester, year = random.choice(terms)
    key = (course_id, semester, year, instructor_id)
    if key in seen_offerings:
        continue
    seen_offerings.add(key)
    cur.execute(
        """INSERT INTO course_offerings (course_id, instructor_id, semester, academic_year, capacity, room, schedule)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (course_id, instructor_id, semester, year, random.choice([25,30,40,50]), 
         f"Room {random.randint(100,499)}", "Mon/Wed 10:00-11:50")
    )
    conn.commit()
    cur.execute("SELECT LAST_INSERT_ID()")
    offering_ids.append(cur.fetchone()[0])

# 8. Enrollments 

seen_pairs = set()
count = 0
while count < 400:
    sid = random.choice(student_ids)
    oid = random.choice(offering_ids)
    if (sid, oid) in seen_pairs:
        continue
    seen_pairs.add((sid, oid))
    cur.execute(
        """INSERT INTO enrollments (student_id, offering_id, enrollment_date, status)
           VALUES (%s,%s,%s,'Enrolled')""",
        (sid, oid, fake.date_between(start_date='-1y', end_date='today'))
    )
    count += 1
conn.commit()

# 9. Tuition payments 

for _ in range(250):
    cur.execute(
        """INSERT INTO tuition_payments (student_id, amount, payment_date, semester, academic_year, payment_method, status)
           VALUES (%s,%s,%s,%s,%s,%s,'Completed')""",
        (random.choice(student_ids), round(random.uniform(1500, 8000), 2), 
         fake.date_time_between(start_date='-1y', end_date='now'), "Fall", 2025, "Credit Card")
    )
conn.commit()

cur.close()
conn.close()
print("Sample data generation complete with trimmed limits.")