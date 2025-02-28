# backend/app/routes/pomodoro.py

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.utils.database import SessionLocal, PomodoroSession, export_pomodoro_logs, calculate_weekly_trends
from pydantic import BaseModel
import asyncio

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for request body validation
class PomodoroStartRequest(BaseModel):
    start_time: datetime
    task_id: int = None  # Optional: Link the session to a task

class PomodoroEndRequest(BaseModel):
    end_time: datetime

# Start a Pomodoro session
@router.post("/pomodoro/start")
def start_pomodoro(request: PomodoroStartRequest, db: Session = Depends(get_db)):
    session = PomodoroSession(start_time=request.start_time, status="running", task_id=request.task_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Pomodoro session started", "session_id": session.id}

# End a Pomodoro session
@router.post("/pomodoro/end/{session_id}")
def end_pomodoro(session_id: int, request: PomodoroEndRequest, db: Session = Depends(get_db)):
    session = db.query(PomodoroSession).filter(PomodoroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pomodoro session not found")
    session.end_time = request.end_time
    session.status = "completed"
    db.commit()
    db.refresh(session)

    # Suggest a break if the session was longer than 25 minutes
    if session.duration() > 25:
        return {"message": "Pomodoro session ended", "duration_minutes": session.duration(), "suggestion": "Take a 5-minute break."}
    return {"message": "Pomodoro session ended", "duration_minutes": session.duration()}

# Get all Pomodoro sessions
@router.get("/pomodoro/")
def get_pomodoro_sessions(db: Session = Depends(get_db)):
    sessions = db.query(PomodoroSession).all()
    return sessions

# Export Pomodoro session logs to a JSON file
@router.get("/pomodoro/export-logs")
def export_logs(db: Session = Depends(get_db)):
    return export_pomodoro_logs(db)

# Get weekly productivity trends
@router.get("/pomodoro/weekly-trends")
def get_weekly_trends(db: Session = Depends(get_db)):
    return calculate_weekly_trends(db)

# WebSocket endpoint for Pomodoro timer
@router.websocket("/pomodoro/timer")
async def pomodoro_timer(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Start a 25-minute Pomodoro session
            for i in range(25 * 60, 0, -1):
                minutes, seconds = divmod(i, 60)
                await websocket.send_text(f"Time remaining: {minutes:02}:{seconds:02}")
                await asyncio.sleep(1)
            await websocket.send_text("Time's up! Take a 5-minute break.")
            await asyncio.sleep(5 * 60)  # 5-minute break
    except Exception as e:
        await websocket.close()
        print(f"WebSocket error: {e}")