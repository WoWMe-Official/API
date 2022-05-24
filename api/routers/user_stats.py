import json
from datetime import datetime
from pickletools import optimize
from pstats import Stats
from typing import Optional
from urllib.request import Request

from api.database.functions import USERDATA_ENGINE, EngineType, sqlalchemy_result
from api.database.models import UserStats
from fastapi import APIRouter, HTTPException, Query, status
from h11 import InformationalResponse
from pydantic import BaseModel
from pydantic.fields import Field
from pymysql import Timestamp
from pyparsing import Opt
from requests import request
from sqlalchemy import BIGINT, DATETIME, TIMESTAMP, VARCHAR, BigInteger, func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, insert, select

router = APIRouter()


class user_stats(BaseModel):
    """
    User Stats base model containing the types and content expected by the database
    """

    ID: Optional[int]
    user_id: Optional[int]
    timestamp: Optional[datetime]
    height: Optional[int]
    weight: Optional[int]
    experience: Optional[int]
    fat_percentage: Optional[int]
    fitness_level: Optional[int]
    fitness_goals: Optional[int]
    ava_dotw: Optional[int]
    ava_hr_start: Optional[datetime]
    ava_hr_end: Optional[datetime]
    pricing_per_hour: Optional[int]


@router.get("/V1/user-stats/", tags=["user", "stats"])
async def get_user_stats(
    token: str,
    ID: Optional[int] = None,
    user_id: Optional[int] = None,
    timestamp: Optional[datetime] = None,
    height: Optional[int] = None,
    weight: Optional[int] = None,
    experience: Optional[int] = None,
    fat_percentage: Optional[int] = None,
    fitness_level: Optional[int] = None,
    fitness_goals: Optional[int] = None,
    ava_dotw: Optional[int] = None,
    ava_hr_start: Optional[datetime] = None,
    ava_hr_end: Optional[datetime] = None,
    pricing_per_hour: Optional[int] = None,
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): token of user accessing content\n
        ID (Optional[int]): ID of entry\n
        user_id (Optional[int]): user ID of entry\n
        timestamp (Optional[datetime]): timestamp of entry\n
        height (Optional[int]): height of the user\n
        weight (Optional[int]): weight of the user\n
        experience (Optional[int]): user experience level\n
        fat_percentage (Optional[int]): user fat percentage\n
        fitness_level (Optional[int]): user fitness level\n
        fitness_goals (Optional[int]): user fitness goals\n
        ava_dotw (Optional[int]): user availability days of the week\n
        ava_hr_start (Optional[datetime]): user availability hour start\n
        ava_hr_end (Optional[datetime]): user availability hour end\n
        pricing_per_hour (Optional[int]): user pricing per hour preference\n
        row_count (Optional[int], optional): row counts to be pulled when requested. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): page count to be set when requested. Defaults to Query(1, ge=1).\n

    Returns:\n
        json: JSON output of value\n
    """

    table = UserStats
    sql: Select = select(table)

    if not ID == None:
        sql = sql.where(table.ID == ID)

    if not user_id == None:
        sql = sql.where(table.user_id == user_id)

    if not height == None:
        sql = sql.where(table.height == height)

    if not weight == None:
        sql = sql.where(table.weight == weight)

    if not experience == None:
        sql = sql.where(table.experience == experience)

    if not fitness_level == None:
        sql = sql.where(table.fitness_level == fitness_level)

    if not fitness_goals == None:
        sql = sql.where(table.fitness_goals == fitness_goals)

    if not fat_percentage == None:
        sql = sql.where(table.fat_percentage == fat_percentage)

    if not ava_dotw == None:
        sql = sql.where(table.ava_dotw == ava_dotw)

    if not ava_hr_start == None:
        sql = sql.where(table.ava_hr_start == ava_hr_start)

    if not ava_hr_end == None:
        sql = sql.where(table.ava_hr_end == ava_hr_end)

    if not pricing_per_hour == None:
        sql = sql.where(table.pricing_per_hour == pricing_per_hour)

    if not timestamp == None:
        sql = sql.where(table.timestamp == timestamp)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/user-stats", tags=["user", "stats"])
async def post_user_stats(user_stats: user_stats) -> json:
    """
    Args:\n
        user_stats (user_stats): user stats model\n

    Returns:\n
        json: {"ok": "ok"}\n
    """

    values = user_stats.dict()
    table = UserStats
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
