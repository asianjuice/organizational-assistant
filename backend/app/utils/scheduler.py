# backend/app/utils/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.utils.email_utils import send_email
from backend.app.utils.database import SessionLocal, Task
from datetime import datetime

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def schedule_reminder(task_id: int, user_email: str, reminder_time: datetime):
    """
    Schedule a reminder for a task.
    """
    scheduler.add_job(
        send_reminder,
        "date",
        run_date=reminder_time,
        args=[task_id, user_email],
    )

def send_reminder(task_id: int, user_email: str):
    """
    Send a reminder email for a task.
    """
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            subject = f"Reminder: {task.title}"
            body = f"Task: {task.title}\nDescription: {task.description}\nDue Date: {task.due_date}"
            send_email(user_email, subject, body)
    finally:
        db.close()