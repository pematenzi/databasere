"""
Generates realistic sample data for the MongoDB collections.
Limits adjusted for a smaller institutional size (150 students).
"""
import random
import os
import sys
from datetime import datetime, timedelta
import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mongo_common import get_db

db = get_db()

# Clear existing collections for a clean run[cite: 4]
for coll in ["course_reviews", "discussion_forums", "notifications", "activity_logs", "assignment_submissions"]:
    db[coll].drop()

random.seed(7)

# ---------------------------------------------------------------
# Pull real IDs from MySQL to keep cross-database references valid[cite: 4]
# ---------------------------------------------------------------
conn = mysql.connector.connect(host="localhost", user="uni_admin", password="uniadmin", database="university_portal")
cur = conn.cursor()

cur.execute("SELECT student_id FROM students")
student_ids = [r[0] for r in cur.fetchall()]

cur.execute("SELECT course_id, course_code FROM courses")
courses = cur.fetchall()
course_ids = [c[0] for c in courses]
course_code_map = {c[0]: c[1] for c in courses}

cur.execute("SELECT instructor_id FROM instructors")
instructor_ids = [r[0] for r in cur.fetchall()]

cur.close()
conn.close()

review_snippets = [
    "Great course, the instructor explained concepts clearly.",
    "Very challenging but rewarding. Learned a lot.",
    "Workload was heavier than expected for the credit hours.",
    "Excellent examples and real-world case studies.",
    "Could use more office hours support.",
    "One of the best courses I've taken so far.",
    "The exams did not match the lecture content well.",
    "Loved the group projects, very hands-on.",
    "Textbook was outdated but lectures were solid.",
    "Instructor was very responsive to questions on the forum."
]
tags_pool = ["heavy-workload", "great-instructor", "recommend", "group-projects",
             "exam-heavy", "practical", "theory-heavy", "good-support"]

def rand_date(days_back=400):
    return datetime.now() - timedelta(days=random.randint(0, days_back), hours=random.randint(0,23))

# ---------------------------------------------------------------
# 1. course_reviews (150 documents)
# ---------------------------------------------------------------
reviews = []
for _ in range(150):
    cid = random.choice(course_ids)
    reviews.append({
        "student_id": random.choice(student_ids),
        "course_id": cid,
        "course_code": course_code_map[cid],
        "rating": random.randint(1, 5),
        "review_text": random.choice(review_snippets),
        "tags": random.sample(tags_pool, k=random.randint(1, 3)),
        "created_at": rand_date()
    })
db.course_reviews.insert_many(reviews)

# ---------------------------------------------------------------
# 2. discussion_forums (75 threads)
# ---------------------------------------------------------------
threads = []
for _ in range(75):
    n_replies = random.randint(0, 6)
    replies = [{
        "author_student_id": random.choice(student_ids),
        "text": random.choice(review_snippets),
        "posted_at": rand_date(200),
        "upvotes": random.randint(0, 15)
    } for _ in range(n_replies)]
    threads.append({
        "course_id": random.choice(course_ids),
        "title": "Discussion Topic",
        "author_student_id": random.choice(student_ids),
        "body": "Posting this to get some clarification / discussion going.",
        "created_at": rand_date(300),
        "tags": random.sample(tags_pool, k=random.randint(0, 2)),
        "replies": replies
    })
db.discussion_forums.insert_many(threads)

# ---------------------------------------------------------------
# 3. notifications (300 documents)
# ---------------------------------------------------------------
notifications = []
for _ in range(300):
    ntype = random.choice(["grade_posted", "payment_due", "enrollment_confirmation"])
    notifications.append({
        "student_id": random.choice(student_ids),
        "type": ntype,
        "message": "Update regarding your student account.",
        "metadata": {"course_id": random.choice(course_ids)},
        "created_at": rand_date(180),
        "read": random.random() > 0.4
    })
db.notifications.insert_many(notifications)

# ---------------------------------------------------------------
# 4. activity_logs (400 documents)
# ---------------------------------------------------------------
logs = []
for _ in range(400):
    logs.append({
        "student_id": random.choice(student_ids),
        "action": random.choice(["login", "submit_assignment", "make_payment"]),
        "timestamp": rand_date(120)
    })
db.activity_logs.insert_many(logs)

# ---------------------------------------------------------------
# 5. assignment_submissions (200 documents)
# ---------------------------------------------------------------
submissions = []
for _ in range(200):
    submissions.append({
        "student_id": random.choice(student_ids),
        "course_id": random.choice(course_ids),
        "assignment_title": "Assignment",
        "submitted_at": rand_date(150),
        "status": "graded"
    })
db.assignment_submissions.insert_many(submissions)

print("MongoDB sample data inserted:")
for coll in ["course_reviews", "discussion_forums", "notifications", "activity_logs", "assignment_submissions"]:
    print(f"  {coll}: {db[coll].count_documents({})} documents")