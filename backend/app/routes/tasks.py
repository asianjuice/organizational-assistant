# backend/app/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.utils.database import SessionLocal, Task, TaskPriority
from datetime import datetime
from typing import Optional
from backend.app.utils.scheduler import schedule_reminder
from backend.app.utils.ai_utils import train_priority_model, predict_task_priority
from backend.app.utils.study_recommendations import analyze_study_sessions

# Create a router for task-related endpoints
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Train the priority model when the application starts
priority_model = train_priority_model()

# Pydantic model for task creation request
class TaskCreateRequest(BaseModel):
    title: str
    description: str
    priority: Optional[TaskPriority] = None  # Optional: User can provide priority or let AI decide
    due_date: datetime
    task_length: Optional[int] = None  # Estimated task length in hours (for AI prioritization)
    reminder_enabled: Optional[bool] = False
    reminder_time: Optional[datetime] = None

# Pydantic model for task update request
class TaskUpdateRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    due_date: datetime
    reminder_enabled: Optional[bool] = False
    reminder_time: Optional[datetime] = None

# Create a new task
@router.post("/")
def create_task(request: TaskCreateRequest, user_email: str = "user@example.com", db: Session = Depends(get_db)):
    """
    Create a new task and schedule a reminder if enabled.
    If no priority is provided, use AI to suggest a priority.
    """
    try:
        # If no priority is provided, task_length is required
        if request.priority is None and request.task_length is None:
            raise HTTPException(
                status_code=400,
                detail="task_length is required when priority is not provided",
            )

        # Calculate days until deadline
        days_until_deadline = (request.due_date - datetime.utcnow()).days

        # If no priority is provided, use AI to predict it
        if request.priority is None:
            # Predict task priority using the AI model
            predicted_priority = predict_task_priority(
                priority_model, days_until_deadline, request.task_length
            )
            # Map the predicted priority to the TaskPriority enum
            priority_map = {"high": TaskPriority.HIGH, "medium": TaskPriority.MEDIUM, "low": TaskPriority.LOW}
            priority = priority_map[predicted_priority]
        else:
            priority = request.priority

        # Create the task
        task = Task(
            title=request.title,
            description=request.description,
            priority=priority,
            due_date=request.due_date,
            reminder_enabled=request.reminder_enabled,
            reminder_time=request.reminder_time,
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        # Schedule a reminder if enabled
        if request.reminder_enabled and request.reminder_time:
            schedule_reminder(task.id, user_email, request.reminder_time)

        return {"message": "Task created successfully", "task_id": task.id, "priority": priority.value}
    except HTTPException as e:
        raise e  # Re-raise HTTPException to return the correct status code
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve all tasks
@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks.
    """
    tasks = db.query(Task).all()
    return tasks

# Update a task
@router.put("/{task_id}")
def update_task(task_id: int, request: TaskUpdateRequest, db: Session = Depends(get_db)):
    """
    Update an existing task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        # Update task fields
        task.title = request.title
        task.description = request.description
        task.priority = request.priority
        task.due_date = request.due_date
        task.reminder_enabled = request.reminder_enabled
        task.reminder_time = request.reminder_time

        db.commit()
        db.refresh(task)

        # Reschedule the reminder if enabled
        if request.reminder_enabled and request.reminder_time:
            schedule_reminder(task.id, "user@example.com", request.reminder_time)

        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db.delete(task)
        db.commit()
        return {"detail": "Task deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve tasks with description "Class"
@router.get("/classes/")
def get_class_tasks(db: Session = Depends(get_db)):
    """
    Retrieve all tasks with the description "Class".
    """
    classes = db.query(Task).filter(Task.description == "Class").all()
    return classes

