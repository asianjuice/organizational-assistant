# backend/app/utils/study_recommendations.py

from datetime import datetime, timedelta
from typing import List, Dict
from backend.app.utils.database import SessionLocal, PomodoroSession

def analyze_study_sessions(user_id: int, db: SessionLocal) -> Dict[str, List[Dict[str, str]]]:
    """
    Analyze the user's study sessions to identify productivity trends.
    """
    # Fetch the user's past study sessions
    sessions = db.query(PomodoroSession).filter(PomodoroSession.user_id == user_id).all()

    if not sessions:
        return {"message": "No study sessions found for this user"}

    # Analyze productivity trends
    productivity_by_hour = {}
    for session in sessions:
        if session.start_time:
            hour = session.start_time.hour
            duration = session.duration()  # Duration in minutes
            if hour in productivity_by_hour:
                productivity_by_hour[hour]["total_duration"] += duration
                productivity_by_hour[hour]["session_count"] += 1
            else:
                productivity_by_hour[hour] = {"total_duration": duration, "session_count": 1}

    # Calculate average productivity per hour
    for hour, data in productivity_by_hour.items():
        data["average_duration"] = data["total_duration"] / data["session_count"]

    # Sort hours by average productivity (descending)
    sorted_hours = sorted(productivity_by_hour.items(), key=lambda x: x[1]["average_duration"], reverse=True)

    # Recommend study times during the most productive hours
    recommendations = []
    for hour, data in sorted_hours[:3]:  # Top 3 most productive hours
        recommendations.append({
            "hour": f"{hour}:00 - {hour + 1}:00",
            "average_duration_minutes": data["average_duration"],
        })

    return {"recommendations": recommendations}