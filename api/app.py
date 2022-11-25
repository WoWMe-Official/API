import api.middleware
from api.config import app
from api.routers import (
    challenge,
    registration,
    profile,
    trainer,
    event,
    dashboard,
    workout,
)

app.include_router(registration.router)
app.include_router(challenge.router)
app.include_router(profile.router)
app.include_router(trainer.router)
app.include_router(event.router)
app.include_router(dashboard.router)
app.include_router(workout.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Workout with Me API. If you're interested in becoming a developer, please contact ferrariictweet@gmail.com!"
    }
