# University Student Portal

A prototype university student portal backend that integrates MySQL and MongoDB data into a unified API.

## Overview

This project demonstrates a hybrid data application with:
- MySQL for relational student, program, course, enrollment, and payment data
- MongoDB for notifications, course reviews, submissions, discussion threads, and activity logs
- A FastAPI service exposing unified dashboard and enrollment endpoints
- A lightweight integration layer that composes data across both databases

## Architecture

- `api.py`: FastAPI application serving the portal endpoints
- `integration_layer.py`: primary application layer that reads from MySQL and MongoDB, and writes enrollments + notifications
- `portal_backend.py`: alternative example integration script showing a similar MySQL/MongoDB bridge
- `mongodb/data_generation/`: MongoDB sample-data generation and shared DB helper
- `mysql/schema/`: schema creation SQL files
- `mysql/data_generation/`: MySQL sample-data generator

## Features

- Unified student dashboard aggregation
- Course enrollment operation with MySQL write and MongoDB notification creation
- CORS-enabled API ready for frontend integration
- Automatic MongoDB `ObjectId` serialization for JSON responses
- MongoDB fallback support using `mongomock` if a local server is unavailable

## Requirements

- Python 3.10+ (or compatible)
- MySQL server
- MongoDB server (recommended) or `mongomock` fallback
- Local database user `uni_admin` with password `uniadmin`

## Setup

1. Install Python dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Create the MySQL database and user:

   ```bash
   mysql -u root -p < mysql/schema/00_init_db.sql
   mysql -u uni_admin -puniadmin < mysql/schema/01_table_creations.sql
   ```

3. Generate sample MySQL data:

   ```bash
   python mysql/data_generation/generate_sample_data.py
   ```

4. Start MongoDB locally, or rely on the in-memory fallback.

5. Populate MongoDB sample data:

   ```bash
   python mongodb/data_generation/generate_sample_data.py
   ```

## Running the API

Start the FastAPI server from the project root:

```bash
uvicorn api:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

- `GET /`
  - Returns a health check message.

- `GET /dashboard/{student_id}`
  - Returns the combined student dashboard, including profile, enrollments, balance, notifications, reviews, and recent submissions.

- `POST /enroll/{student_id}/{offering_id}`
  - Enrolls the student in the specified course offering and creates a confirmation notification.

## Database Notes

- MySQL database: `university_portal`
- MongoDB database: `university_portal`
- MongoDB collections used by the primary integration layer:
  - `notifications`
  - `course_reviews`
  - `assignment_submissions`

## Helpful Notes

- The primary app entrypoint is `api.py`.
- `integration_layer.py` contains the composite read/write logic.
- `portal_backend.py` is a separate example script and not required to run the API.
- If MongoDB is unavailable, `mongodb/data_generation/mongo_common.py` falls back to `mongomock`.

## Project Structure

- `api.py` - FastAPI API definition
- `integration_layer.py` - MySQL + MongoDB integration logic
- `portal_backend.py` - alternative backend example
- `requirements.txt` - Python package dependencies
- `mysql/schema/` - SQL schema setup files
- `mysql/data_generation/` - MySQL sample data generator
- `mongodb/data_generation/` - MongoDB sample data generator and helper


