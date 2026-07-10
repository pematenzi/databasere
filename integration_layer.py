"""
University Student Portal - Application (Integration) Layer
Updated with ObjectId serialization fix.
"""
import os
import sys
import mysql.connector
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mongodb", "data_generation"))
from mongo_common import get_db

mongo_db = get_db()

def get_mysql_conn():
    return mysql.connector.connect(host="localhost", user="uni_admin", password="uniadmin",
                                   database="university_portal")

def get_student_dashboard(student_id: int) -> dict:
    """
    Composite read: pulls data from MySQL and MongoDB.
    Includes explicit ObjectId to string conversion.
    """
    conn = get_mysql_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT s.student_id, s.first_name, s.last_name, s.email, s.gpa, s.status,
               p.program_name, p.degree_level
        FROM students s JOIN programs p ON s.program_id = p.program_id
        WHERE s.student_id = %s
    """, (student_id,))
    profile = cur.fetchone()

    cur.execute("""
        SELECT c.course_code, c.course_name, co.semester, co.academic_year, e.grade, e.status
        FROM enrollments e
        JOIN course_offerings co ON e.offering_id = co.offering_id
        JOIN courses c ON co.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY co.academic_year DESC
    """, (student_id,))
    enrollments = cur.fetchall()

    cur.execute("""
        SELECT SUM(amount) AS outstanding
        FROM tuition_payments
        WHERE student_id = %s AND status IN ('Pending','Failed')
    """, (student_id,))
    balance = cur.fetchone()["outstanding"] or 0
    cur.close()
    conn.close()

    # --- MongoDB side: Fetch and convert ObjectIds to strings ---
    def clean_mongo_docs(docs):
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return docs

    unread_notifications = clean_mongo_docs(list(mongo_db.notifications.find(
        {"student_id": student_id, "read": False}
    ).sort("created_at", -1).limit(5)))

    my_reviews = clean_mongo_docs(list(mongo_db.course_reviews.find({"student_id": student_id})))

    recent_submissions = clean_mongo_docs(list(mongo_db.assignment_submissions.find(
        {"student_id": student_id}
    ).sort("submitted_at", -1).limit(5)))

    return {
        "profile": profile,
        "enrollments": enrollments,
        "outstanding_balance": float(balance),
        "unread_notifications": unread_notifications,
        "reviews_written": my_reviews,
        "recent_submissions": recent_submissions,
    }

def enroll_student_in_course(student_id: int, offering_id: int) -> dict:
    """
    Composite write: writes to MySQL then triggers MongoDB side effect.
    """
    conn = get_mysql_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO enrollments (student_id, offering_id, enrollment_date, status) "
            "VALUES (%s, %s, CURDATE(), 'Enrolled')",
            (student_id, offering_id)
        )
        conn.commit()
        enrollment_id = cur.lastrowid
    except mysql.connector.Error as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cur.close()
        conn.close()

    mongo_db.notifications.insert_one({
        "student_id": student_id,
        "type": "enrollment_confirmation",
        "message": "Your enrollment has been confirmed.",
        "metadata": {"offering_id": offering_id},
        "created_at": datetime.now(),
        "read": False
    })
    return {"success": True, "enrollment_id": enrollment_id}