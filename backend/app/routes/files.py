# backend/app/routes/files.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from datetime import datetime
import csv
from ics import Calendar
from backend.app.utils.database import SessionLocal, Task
from sqlalchemy.orm import Session

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to parse CSV files
def parse_csv(file):
    classes = []
    reader = csv.DictReader(file)
    for row in reader:
        classes.append({
            "title": row["title"],
            "start_time": datetime.fromisoformat(row["start_time"]),
            "end_time": datetime.fromisoformat(row["end_time"])
        })
    return classes

# Function to parse ICS files
def parse_ics(file):
    calendar = Calendar(file.read().decode("utf-8"))
    classes = []
    for event in calendar.events:
        classes.append({
            "title": event.name,
            "start_time": event.begin.datetime,
            "end_time": event.end.datetime
        })
    return classes

# Endpoint to upload class schedule
@router.post("/upload-schedule/")
async def upload_schedule(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if file.filename.endswith(".csv"):
            classes = parse_csv(file.file)
        elif file.filename.endswith(".ics"):
            classes = parse_ics(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # Store class timings in the database
        for cls in classes:
            db_task = Task(
                title=cls["title"],
                description="Class",
                priority="medium",
                due_date=cls["start_time"],
                status="scheduled"
            )
            db.add(db_task)
        db.commit()

        return {"message": "Class schedule uploaded and tasks created", "classes": classes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))