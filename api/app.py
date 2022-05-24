import api.middleware
from api.config import app
from api.database.models import UserInformation
from api.routers import (
    request_history,
    trainer_acception_status,
    user_chat,
    user_information,
    user_rating_history,
    user_stats,
    user_token,
    users,
)

app.include_router(request_history.router)
app.include_router(trainer_acception_status.router)
app.include_router(user_chat.router)
app.include_router(user_information.router)
app.include_router(user_rating_history.router)
app.include_router(user_stats.router)
app.include_router(user_token.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Workout with Me API. If you're interested in becoming a developer, please contact ferrariictweet@gmail.com!"
    }
