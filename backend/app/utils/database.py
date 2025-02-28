# backend/app/utils/database.py

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import sessionmaker
from .config import Base, engine, SessionLocal
import enum
from datetime import datetime, timedelta
import json

# Define an enumeration for task priority
class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Define the Task model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime)
    status = Column(String, default="pending")

# Define the PomodoroSession model
class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="stopped")
    task_id = Column(Integer, ForeignKey("tasks.id"))  # Link to a task

    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60  # Duration in minutes
        return 0

# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Function to create a new task
def create_task(db: SessionLocal, title: str, description: str, priority: TaskPriority, due_date: datetime):
    db_task = Task(title=title, description=description, priority=priority, due_date=due_date)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Function to create a new Pomodoro session
def create_pomodoro_session(db: SessionLocal, start_time: datetime, task_id: int = None):
    session = PomodoroSession(start_time=start_time, status="running", task_id=task_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

# Function to end a Pomodoro session
def end_pomodoro_session(db: SessionLocal, session_id: int, end_time: datetime):
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        return None
    session.end_time = end_time
    session.status = "completed"
    db.commit()
    db.refresh(session)
    return session

# Function to export Pomodoro session logs to a JSON file
def export_pomodoro_logs(db: SessionLocal, file_path: str = "pomodoro_logs.json"):
    sessions = db.query(PomodoroSession).all()
    logs = []
    for session in sessions:
        logs.append({
            "id": session.id,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_minutes": session.duration(),
            "status": session.status,
            "task_id": session.task_id
        })
    with open(file_path, "w") as f:
        json.dump(logs, f, indent=4)
    return {"message": f"Pomodoro logs exported to {file_path}"}

# Function to calculate weekly productivity trends
def calculate_weekly_trends(db: SessionLocal):
    sessions = db.query(PomodoroSession).all()
    weekly_data = {}

    for session in sessions:
        if session.start_time:
            week_start = session.start_time - timedelta(days=session.start_time.weekday())
            week_key = week_start.strftime("%Y-%m-%d")

            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "total_time_minutes": 0,
                    "session_count": 0,
                    "average_duration_minutes": 0
                }

            weekly_data[week_key]["total_time_minutes"] += session.duration()
            weekly_data[week_key]["session_count"] += 1

    # Calculate average duration per week
    for week in weekly_data:
        weekly_data[week]["average_duration_minutes"] = (
            weekly_data[week]["total_time_minutes"] / weekly_data[week]["session_count"]
        )

    return weekly_data