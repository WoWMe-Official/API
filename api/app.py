import api.middleware
from api.config import app

from api.routers import request_history, trainer_acception_status

app.include_router(request_history.router)
app.include_router(trainer_acception_status.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Workout with Me API. If you're interested in becoming a developer, please contact ferrariictweet@gmail.com!"
    }
