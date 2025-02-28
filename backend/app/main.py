# backend/app/main.py

from fastapi import FastAPI
from backend.app.routes import tasks, pomodoro

app = FastAPI()

# Include the routers
app.include_router(tasks.router)
app.include_router(pomodoro.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Organizational Assistant API"}