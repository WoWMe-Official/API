import json
from cgitb import text
from datetime import datetime
from optparse import Option
from pickletools import optimize
from pstats import Stats
from typing import Optional
from urllib.request import Request

from api.database.functions import USERDATA_ENGINE, EngineType, sqlalchemy_result
from api.database.models import Users
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


class users(BaseModel):
    """
    Users base model containing the types and content expected by the database
    """

    user_id: Optional[int]
    login: Optional[str]
    password: Optional[str]
    timestamp: Optional[datetime]


@router.get("/V1/users/", tags=["user"])
async def get_users(
    token: str,
    user_id: Optional[int] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): token of the authorized user\n
        user_id (Optional[int], optional): user id. Defaults to None.\n
        login (Optional[str], optional): login username. Defaults to None.\n
        password (Optional[str], optional): hashed/salted password to be checked against on login. Defaults to None.\n
        timestamp (Optional[datetime], optional): timestamp of creation. Defaults to None.\n
        row_count (Optional[int], optional): row count to be chosen at time of get. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): page selection. Defaults to Query(1, ge=1).\n

    Returns:\n
        json: output as listed above\n
    """

    table = Users
    sql: Select = select(table)

    if not token == None:
        sql = sql.where(table.token == token)

    if not user_id == None:
        sql = sql.where(table.user_id == user_id)

    if not login == None:
        sql = sql.where(table.login == login)

    if not password == None:
        sql = sql.where(table.password == password)

    if not timestamp == None:
        sql = sql.where(table.timestamp == timestamp)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/users", tags=["user"])
async def post_users(users: users) -> json:
    """
    Args:\n
        users (users): users model\n

    Returns:\n
        json: {"ok": "ok"}\n
    """

    values = users.dict()
    table = Users
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
