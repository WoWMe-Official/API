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
from api.database.models import TrainerAcceptionStatus
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


class trainer_acception_status(BaseModel):
    """
    trainer_acception_status base model containing the types and content expected by the database
    """

    ID: Optional[int]
    user_id: int
    is_trainer: Optional[bool] = None
    is_pending: Optional[bool] = None
    timestamp: Optional[datetime] = None


@router.get("/V1/trainer-acception-status/",
            tags=["trainer", "trainer acception status"])
async def get_trainer_acception_status(
    token: str,
    login: str,
    user_id: int,
    ID: Optional[int] = None,
    is_trainer: Optional[bool] = None,
    is_pending: Optional[bool] = None,
    timestamp: Optional[datetime] = None,
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): Token of the user accessing the content\n
        ID (Optional[int]): ID of the relevant entry\n
        user_id (int): user id of the entry\n
        is_trainer (Optional[bool], optional): If the entry is for a trainer, or not. Defaults to None.\n
        is_pending (Optional[bool], optional): If the user is awaiting to be accepted. Defaults to None.\n
        timestamp (Optional[datetime], optional): Creation timestamp. Defaults to None.\n
        row_count (Optional[int], optional): How many rows should be pulled. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): What page should be pulled. Defaults to Query(1, ge=1).\n

    Returns:\n
        json: Json response containing the relevant information.\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    table = TrainerAcceptionStatus
    sql: Select = select(table)

    if ID is not None:
        sql = sql.where(table.ID == ID)

    if user_id is not None:
        sql = sql.where(table.user_id == user_id)

    if is_trainer is not None:
        sql = sql.where(table.is_trainer == is_trainer)

    if is_pending is not None:
        sql = sql.where(table.is_pending == is_pending)

    if timestamp is not None:
        sql = sql.where(table.timestamp == timestamp)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/trainer-acception-status",
             tags=["trainer", "trainer acception status"])
async def post_trainer_acception_status(
    login: str,
    token: str,
    trainer_acception_status: trainer_acception_status,
) -> json:
    """
    Args:\n
        trainer_acception_status (trainer_acception_status): A dictionary containing the trainer_acception_status payload\n

    Returns:\n
        json: {"ok": "ok"}\n
    """
    if not await verify_token(login=login, token=token, access_level=9):
        return
    values = trainer_acception_status.dict()
    table = TrainerAcceptionStatus
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
