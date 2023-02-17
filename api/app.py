import api.middleware
import logging
from api.config import app, redis_client
from api.routers import (
    account,
    challenge,
    dashboard,
    event,
    profile,
    trainer,
    workout,
    images,
    inbox,
)

logger = logging.getLogger(__name__)

app.include_router(account.router)
app.include_router(challenge.router)
app.include_router(profile.router)
app.include_router(trainer.router)
app.include_router(event.router)
app.include_router(dashboard.router)
app.include_router(workout.router)
app.include_router(images.router)
app.include_router(inbox.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Workout with Me API. If you're interested in becoming a developer, please contact ferrariictweet@gmail.com!"
    }


@app.on_event("startup")
async def startup():
    # check redis server
    if await redis_client.ping():
        logger.info("REDIS SERVER CONNECTED!")
    else:
        logger.fatal("REDIS SERVER IS NOT ACCESSIBLE!")
