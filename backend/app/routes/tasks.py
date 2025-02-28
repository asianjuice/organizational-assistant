# backend/app/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.utils.database import SessionLocal, Task, TaskPriority, create_task
from datetime import datetime

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for request body validation
class TaskCreateRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    due_date: datetime

# Create a new task
@router.post("/tasks/")
async def add_task(request: TaskCreateRequest, db: Session = Depends(get_db)):
    task = create_task(db, request.title, request.description, request.priority, request.due_date)
    return task

# Retrieve all tasks
@router.get("/tasks/")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

# Update a task
class TaskUpdateRequest(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    due_date: datetime

@router.put("/tasks/{task_id}")
async def update_task(task_id: int, request: TaskUpdateRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = request.title
    task.description = request.description
    task.priority = request.priority
    task.due_date = request.due_date
    db.commit()
    db.refresh(task)
    return task

# Delete a task
@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}