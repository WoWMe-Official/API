import hashlib
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

import api.routers.models.workout as workout_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Stats, StatWorkoutHash, Workout, WorkoutPlan
from api.routers.functions.general import get_token_user_id

router = APIRouter()


def hash(string):
    return hashlib.sha256(string.encode()).hexdigest()


@router.post("/v1/workout/{token}", tags=["workout"])
async def post_workout_plan(
    token: str, workout_plan: workout_models.workout_plan
) -> json:

    uuid = await get_token_user_id(token=token)

    stat_values = []
    stat_hashes = []
    for s in workout_plan.global_stats:
        s.hash = hash(f"{s.title}_{s.stat}")
        s.uuid = uuid
        stat_values.append(s.dict())
        stat_hashes.append(s.hash)

    workout_plan_values = []
    workout_hashes = []
    for wp in workout_plan.workout_plan:
        wp.hash = hash(f"{wp.reps}_{wp.workout}_{wp.weight}")
        wp.uuid = uuid
        workout_plan_values.append(wp.dict())
        workout_hashes.append(wp.hash)

    stat_workout_hash_table_values = []
    for s, w in list(zip(stat_hashes, workout_hashes)):
        d = dict()
        d["uuid"] = uuid
        d["stat"] = s
        d["workout"] = w
        stat_workout_hash_table_values.append(d)

    insert_stat_values = insert(Stats).values(stat_values)
    insert_workout_values = insert(Workout).values(workout_plan_values)
    insert_workout_plan = insert(WorkoutPlan).values(
        name=workout_plan.name,
        rating=workout_plan.rating,
        uuid=uuid,
        fitness_level=workout_plan.fitness_level,
        workouts_completed=workout_plan.workouts_completed,
    )
    insert_stat_workout_hash_table = insert(StatWorkoutHash).values(
        stat_workout_hash_table_values
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_stat_values)
            await session.execute(insert_workout_values)
            await session.execute(insert_workout_plan)
            await session.execute(insert_stat_workout_hash_table)

    raise HTTPException(status_code=status.HTTP_201_CREATED, detail=f"{uuid}")


@router.get("/v1/workout/{token}/{user_id}", tags=["workout"])
async def get_workout_plan(token: str, user_id: str) -> json:

    uuid_token = await get_token_user_id(token=token)

    select_workout_plan = select(WorkoutPlan).where(WorkoutPlan.uuid == user_id)
    select_workout_values = select(Workout).where(Workout.uuid == user_id)
    select_stat_values = select(Stats).where(Stats.uuid == user_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            workout_plan_result = await session.execute(select_workout_plan)
            workout_result = await session.execute(select_workout_values)
            stat_result = await session.execute(select_stat_values)

    workout_plan_result = sqlalchemy_result(workout_plan_result)
    workout_result = sqlalchemy_result(workout_result)
    stat_result = sqlalchemy_result(stat_result)

    workout_plan_result = workout_plan_result.rows2dict()
    workout_result = workout_result.rows2dict()
    stat_result = stat_result.rows2dict()
    response_dict = dict()
    response_dict["workout"] = workout_result
    response_dict["workout_plan"] = workout_plan_result
    response_dict["global_stats"] = stat_result

    raise HTTPException(status_code=status.HTTP_200_OK, detail=response_dict)
