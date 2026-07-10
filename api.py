import json
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from integration_layer import get_student_dashboard, enroll_student_in_course

# 1. Custom JSON Encoder to handle MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

# 2. Custom JSONResponse that uses the encoder
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, cls=MongoJSONEncoder).encode("utf-8")

app = FastAPI(title="University Student Portal API", default_response_class=CustomJSONResponse)

# 3. Add CORS Middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the University Portal API! The system is online."}

@app.get("/dashboard/{student_id}")
def get_dashboard(student_id: int):
    """
    Fetches the unified student dashboard by merging MySQL and MongoDB data.
    """
    try:
        data = get_student_dashboard(student_id)
        
        if not data.get("profile"):
            raise HTTPException(status_code=404, detail="Student not found")
            
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enroll/{student_id}/{offering_id}")
def enroll_student(student_id: int, offering_id: int):
    """
    Enrolls a student in a course and sends a confirmation alert.
    """
    result = enroll_student_in_course(student_id, offering_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result