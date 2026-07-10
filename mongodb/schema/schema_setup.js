db = db.getSiblingDB("university_portal");


db.createCollection("course_reviews", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["student_id", "course_id", "rating", "review_text", "created_at"],
      properties: {
        student_id: { bsonType: "int", description: "FK reference to MySQL students.student_id" },
        course_id:  { bsonType: "int", description: "FK reference to MySQL courses.course_id" },
        course_code: { bsonType: "string" },
        rating:     { bsonType: "int", minimum: 1, maximum: 5 },
        review_text: { bsonType: "string" },
        tags:       { bsonType: "array", items: { bsonType: "string" } },
        created_at: { bsonType: "date" }
      }
    }
  }
});
db.course_reviews.createIndex({ course_id: 1 });
db.course_reviews.createIndex({ student_id: 1 });
db.course_reviews.createIndex({ rating: -1 });


db.createCollection("discussion_forums", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["course_id", "title", "author_student_id", "created_at", "replies"],
      properties: {
        course_id: { bsonType: "int" },
        title: { bsonType: "string" },
        author_student_id: { bsonType: "int" },
        body: { bsonType: "string" },
        created_at: { bsonType: "date" },
        tags: { bsonType: "array", items: { bsonType: "string" } },
        replies: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["author_student_id", "text", "posted_at"],
            properties: {
              author_student_id: { bsonType: "int" },
              text: { bsonType: "string" },
              posted_at: { bsonType: "date" },
              upvotes: { bsonType: "int" }
            }
          }
        }
      }
    }
  }
});
db.discussion_forums.createIndex({ course_id: 1, created_at: -1 });
db.discussion_forums.createIndex({ author_student_id: 1 });


db.createCollection("notifications", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["student_id", "type", "message", "created_at", "read"],
      properties: {
        student_id: { bsonType: "int" },
        type: { enum: ["grade_posted", "payment_due", "enrollment_confirmation", "announcement", "system"] },
        message: { bsonType: "string" },
        metadata: { bsonType: "object" },
        created_at: { bsonType: "date" },
        read: { bsonType: "bool" }
      }
    }
  }
});
db.notifications.createIndex({ student_id: 1, read: 1 });
db.notifications.createIndex({ created_at: -1 });


db.createCollection("activity_logs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["student_id", "action", "timestamp"],
      properties: {
        student_id: { bsonType: "int" },
        action: { bsonType: "string" },
        ip_address: { bsonType: "string" },
        user_agent: { bsonType: "string" },
        details: { bsonType: "object" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});
db.activity_logs.createIndex({ timestamp: -1 });
db.activity_logs.createIndex({ student_id: 1, timestamp: -1 });


db.createCollection("assignment_submissions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["student_id", "course_id", "assignment_title", "submitted_at"],
      properties: {
        student_id: { bsonType: "int" },
        course_id: { bsonType: "int" },
        assignment_title: { bsonType: "string" },
        submitted_at: { bsonType: "date" },
        file_metadata: {
          bsonType: "object",
          properties: {
            filename: { bsonType: "string" },
            size_kb: { bsonType: "int" },
            file_type: { bsonType: "string" }
          }
        },
        feedback: {
          bsonType: "object",
          properties: {
            grader_instructor_id: { bsonType: "int" },
            score: { bsonType: "double" },
            comments: { bsonType: "string" },
            graded_at: { bsonType: "date" }
          }
        },
        status: { enum: ["submitted", "late", "graded", "resubmitted"] }
      }
    }
  }
});
db.assignment_submissions.createIndex({ student_id: 1, course_id: 1 });
db.assignment_submissions.createIndex({ status: 1 });

print("MongoDB collections and indexes created successfully.");
