# backend/app/main.py

from fastapi import FastAPI
from backend.app.routes import tasks, pomodoro, calendar, files, notes, habits_goals, study

# Create the FastAPI app
app = FastAPI()

# Include the routers
app.include_router(tasks.router)
app.include_router(pomodoro.router)
app.include_router(calendar.router)
app.include_router(files.router)
app.include_router(notes.router)
app.include_router(habits_goals.router)
app.include_router(study.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Organizational Assistant API"}