import json

from fastapi import APIRouter
from sqlalchemy.sql.expression import select, update
import api.routers.models.workout as workout_models

router = APIRouter()


@router.post("/v1/workout/{token}", tags=["workout"])
async def post_workout_plan(
    token: str, workout_plan: workout_models.workout_plan
) -> json:
    return


@router.get("/v1/workout/{token}/{user_id}", tags=["workout"])
async def get_workout_plan(token: str, user_id: str) -> json:
    """
    Params:
    {
    Token: string,
    User id: number,
    }
    Returns:
    {
    Name: string,
    Rating: number,
    Number of workouts completed: number,
    Fitness level: string,
    Global stats: array: { title: string, stat: number },
    Workout plan: array: array: {workout: string, repts: string, weight: number}
    }
    """
