from datetime import datetime
import json
from typing import Optional
from urllib.request import Request

from api.database.functions import (
    USERDATA_ENGINE,
    EngineType,
    sqlalchemy_result,
    verify_token,
)
from api.database.models import RequestHistory
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from pymysql import Timestamp
from sqlalchemy import DATETIME, TIMESTAMP, func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, select, insert

router = APIRouter()


class request_history(BaseModel):
    """
    Request History base model containing the types and content expected by the database
    """

    s_user_id: int
    r_user_id: int
    timestamp_START: Optional[datetime] = None
    timestamp_DEAD: Optional[datetime] = None
    timestamp_start_session: Optional[datetime] = None
    timestamp_end_session: Optional[datetime] = None
    price_per_hour: Optional[int] = Query(..., ge=0, le=1000)
    fitness_categories: Optional[int] = Query(None, ge=0)
    status: Optional[int] = Query(0, ge=0, le=2)


@router.get("/V1/request-history/", tags=["request history"])
async def get_request_history(
    token: str,
    login: str,
    s_user_id: int,
    r_user_id: int,
    timestamp_START: Optional[datetime] = None,
    timestamp_DEAD: Optional[datetime] = None,
    timestamp_start_session: Optional[datetime] = None,
    timestamp_end_session: Optional[datetime] = None,
    price_per_hour: Optional[int] = Query(..., ge=0, le=1000),
    fitness_categories: Optional[int] = Query(None, ge=0),
    status: Optional[int] = Query(0, ge=0, le=2),
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): User token for verification of request retrival.\n
        s_user_id (int): Sending user ID, or the user Sending the Request.\n
        r_user_id (int): Receiving user ID, or the user Receiving the Request.\n
        timestamp_START (Optional[datetime], optional): The request initial start time, in datetime format. Defaults to None.\n
        timestamp_DEAD (Optional[datetime], optional): The request dead time, when the request should be removed from entries. Defaults to None.\n
        timestamp_start_session (Optional[datetime], optional): Session start time, this should be activated when the session begins. Defaults to None.\n
        timestamp_end_session (Optional[datetime], optional): Session end time, this should be activated once the session finishes. Defaults to None.\n
        price_per_hour (Optional[int], optional): Agreed price per hour of the arrangement. Defaults to Query(..., ge=0, le=1000).\n
        fitness_categories (Optional[int], optional): fitness category as an integer, this corresponds with a pre-known category. Defaults to Query(None, ge=0).\n
        status (Optional[int], optional): Status of the agreement. 0 : Pending, 1 : Accepted, 2 : Declined. Defaults to Query(0, ge=0, le=2).\n
        row_count (Optional[int], optional): How many rows to pull from the database. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): Which page to pull from the request. Defaults to Query(1, ge=1).\n

    Returns:\n
        json : A json containing the relevant information from the request.\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    table = RequestHistory
    sql: Select = select(table)

    if not s_user_id == None:
        sql = sql.where(table.s_user_id == s_user_id)

    if not r_user_id == None:
        sql = sql.where(table.r_user_id == r_user_id)

    if not timestamp_START == None:
        sql = sql.where(table.timestamp_START == timestamp_START)

    if not timestamp_DEAD == None:
        sql = sql.where(table.timestamp_DEAD == timestamp_DEAD)

    if not timestamp_start_session == None:
        sql = sql.where(table.timestamp_start_session == timestamp_start_session)

    if not timestamp_end_session == None:
        sql = sql.where(table.timestamp_end_session == timestamp_end_session)

    if not price_per_hour == None:
        sql = sql.where(table.price_per_hour == price_per_hour)

    if not fitness_categories == None:
        sql = sql.where(table.fitness_categories == fitness_categories)

    if not status == None:
        sql = sql.where(table.status == status)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    # execute query
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/request-history", tags=["request history"])
async def post_request_history(
    login: str, token: str, request_history: request_history
) -> json:
    """
    Args:\n
        request_history (request_history): Json containing the relevant elements of a request-history entry.\n

    Returns:\n
        json: {"ok": "ok"}\n
    """
    if not await verify_token(login=login, token=token, access_level=9):
        return
    values = request_history.dict()
    table = RequestHistory
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
