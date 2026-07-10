import mysql.connector
from pymongo import MongoClient

# 1. DATABASE CONNECTIONS

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="uni_admin",          # Change if your MySQL user is different
        password="uniadmin",  # Change to your MySQL password
        database="university_portal"
    )

def get_mongo_collection():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["university_portal_nosql"]
    return db["course_materials"]

# 2. CORE LOGIC: Fetch Student Dashboard

def get_student_dashboard(student_id):
    mysql_conn = get_mysql_connection()
    cursor = mysql_conn.cursor(dictionary=True)
    mongo_collection = get_mongo_collection()
    
    dashboard = {
        "student_info": {},
        "courses": []
    }

    try:
        # STEP 1: Query MySQL for the student and their enrollments
        query = """
            SELECT s.first_name, s.last_name, c.course_id, c.course_code, c.course_name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE s.student_id = %s
        """
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()

        if not results:
            print(f"No student found with ID {student_id}")
            return None

        # Set the basic student info (from the first row)
        dashboard["student_info"] = {
            "name": f"{results[0]['first_name']} {results[0]['last_name']}",
            "student_id": student_id
        }

        # STEP 2: Loop through each enrolled course
        for row in results:
            course_id = row['course_id']
            course_code = row['course_code']
            
            # THE BRIDGE: Query MongoDB for the materials using the MySQL course_id
            materials = mongo_collection.find_one({"mysql_course_id": course_id})
            
            course_data = {
                "course_code": course_code,
                "course_name": row['course_name'],
                "syllabus": None,
                "modules": []
            }
            
            # If MongoDB has materials for this course, attach them
            if materials:
                course_data["syllabus"] = materials.get("syllabus")
                course_data["modules"] = materials.get("modules", [])
                
            dashboard["courses"].append(course_data)
            
        return dashboard

    finally:
        cursor.close()
        mysql_conn.close()

# 3. RUN THE TEST

if __name__ == "__main__":
    # Let's test with Alice Smith (student_id = 1)
    print("Fetching dashboard for Student ID: 1...\n")
    
    student_data = get_student_dashboard(student_id=1)
    
    if student_data:
        print(f"--- Welcome, {student_data['student_info']['name']} ---")
        print("Your Enrolled Courses:")
        
        for course in student_data["courses"]:
            print(f"\n> {course['course_code']}: {course['course_name']}")
            
            if course["syllabus"]:
                print(f"  Materials Found! Modules available: {len(course['modules'])}")
            else:
                print("  (No materials uploaded yet)")