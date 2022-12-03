import json

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from pymysql import Timestamp
import datetime

from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens
from sqlalchemy.sql.expression import select, update
from api.database.database import USERDATA_ENGINE
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update

router = APIRouter()


@router.get("/v1/workout/{token}/{user_id}", tags=['workout'])
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
