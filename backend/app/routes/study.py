# backend/app/routes/study.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.utils.database import SessionLocal
from backend.app.utils.study_recommendations import analyze_study_sessions

# Create a router for study-related endpoints
router = APIRouter(prefix="/api/study", tags=["study"])

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get study session recommendations
@router.get("/recommendations/{user_id}")
def get_study_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Get study session recommendations for a user.
    """
    try:
        recommendations = analyze_study_sessions(user_id, db)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))