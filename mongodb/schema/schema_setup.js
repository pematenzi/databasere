// =====================================================================
// University Student Portal - MongoDB Schema Setup
// Run with: mongosh university_portal < schema_setup.js
// (Standard mongosh/MongoDB syntax - deploy to local mongod or Atlas)
// =====================================================================
db = db.getSiblingDB("university_portal");

// ---------------------------------------------------------------
// 1. course_reviews - semi-structured, one doc per review
//    Embeds: nothing nested (flat, high write volume, read by course_id)
//    References: student_id, course_id (foreign keys back to MySQL)
// ---------------------------------------------------------------
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

// ---------------------------------------------------------------
// 2. discussion_forums - discussion threads with EMBEDDED replies
//    Justification: replies are always read together with the parent
//    thread, are bounded in number (typically < few hundred), and are
//    never queried independently of the thread -> embedding is correct.
// ---------------------------------------------------------------
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

// ---------------------------------------------------------------
// 3. notifications - varied/polymorphic structure per notification type
//    Referenced by student_id only (no embedding - unbounded, high volume,
//    frequently queried/paginated/deleted independently per student).
// ---------------------------------------------------------------
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

// ---------------------------------------------------------------
// 4. activity_logs - unstructured, high-volume, append-only, time-series-like
//    No relational integrity needed; optimized for write throughput and
//    time-range queries. No embedding relationship - fully independent docs.
// ---------------------------------------------------------------
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

// ---------------------------------------------------------------
// 5. assignment_submissions - semi-structured with EMBEDDED feedback
//    Justification: feedback is 1-2 small subdocuments per submission,
//    always fetched with the submission -> embed. File metadata (not the
//    binary itself) is embedded since it's small & always shown together.
// ---------------------------------------------------------------
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
