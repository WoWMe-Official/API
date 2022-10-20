import api.middleware
from api.config import app
from api.routers import (
    registration,
)

app.include_router(registration.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Workout with Me API. If you're interested in becoming a developer, please contact ferrariictweet@gmail.com!"
    }
