# backend/app/main.py

from fastapi import FastAPI
from backend.app.routes import tasks, pomodoro, calendar #files
app = FastAPI()

# Include the routers
app.include_router(tasks.router)
app.include_router(pomodoro.router)
app.include_router(calendar.router)
#app.include_router(files.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Organizational Assistant API"}