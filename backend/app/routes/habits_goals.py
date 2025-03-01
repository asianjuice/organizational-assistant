from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.utils.database import SessionLocal, Goal, Habit

# Create a router for habit and goal-related endpoints
router = APIRouter(prefix="/api/habits-goals", tags=["habits-goals"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request validation
class GoalCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    user_id: int

class HabitCreateRequest(BaseModel):
    title: str
    description: str
    user_id: int

class HabitCompleteRequest(BaseModel):
    habit_id: int
    completed_at: datetime

# Create a new goal
@router.post("/goals/")
def create_goal(request: GoalCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new goal.
    """
    try:
        goal = Goal(
            title=request.title,
            description=request.description,
            category=request.category,
            user_id=request.user_id,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return {"message": "Goal created successfully", "goal_id": goal.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Create a new habit
@router.post("/habits/")
def create_habit(request: HabitCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new habit.
    """
    try:
        habit = Habit(
            title=request.title,
            description=request.description,
            user_id=request.user_id,
        )
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return {"message": "Habit created successfully", "habit_id": habit.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve all goals for a user
@router.get("/goals/{user_id}")
def get_goals(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all goals for a user.
    """
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    if not goals:
        raise HTTPException(status_code=404, detail="No goals found for this user")
    return goals

# Retrieve all habits for a user
@router.get("/habits/{user_id}")
def get_habits(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all habits for a user.
    """
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    if not habits:
        raise HTTPException(status_code=404, detail="No habits found for this user")
    return habits

# Mark a habit as completed
@router.post("/habits/complete/")
def complete_habit(request: HabitCompleteRequest, db: Session = Depends(get_db)):
    """
    Mark a habit as completed and update the streak.
    """
    habit = db.query(Habit).filter(Habit.id == request.habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    try:
        # Check if the habit was completed yesterday (to maintain the streak)
        if habit.last_completed and (request.completed_at - habit.last_completed).days == 1:
            habit.streak += 1
        else:
            habit.streak = 1  # Reset streak if not completed consecutively

        habit.last_completed = request.completed_at
        db.commit()
        db.refresh(habit)
        return {"message": "Habit completed successfully", "streak": habit.streak}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))