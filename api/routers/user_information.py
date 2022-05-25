import json
from datetime import datetime
from typing import Optional
from urllib.request import Request

from api.database.functions import (
    USERDATA_ENGINE,
    EngineType,
    sqlalchemy_result,
    verify_token,
)
from api.database.models import UserInformation
from fastapi import APIRouter, HTTPException, Query, status
from h11 import InformationalResponse
from pydantic import BaseModel
from pydantic.fields import Field
from pymysql import Timestamp
from pyparsing import Opt
from sqlalchemy import BIGINT, DATETIME, TIMESTAMP, VARCHAR, BigInteger, func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, insert, select

router = APIRouter()


class user_information(BaseModel):
    """
    User information base model containing the types and content expected by the database
    """

    ID: Optional[int]
    user_id: Optional[int]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    birthday: Optional[datetime]
    gender: Optional[int]
    location: Optional[str]
    timestamp: Optional[datetime]
    email: Optional[str]
    phone: Optional[str]
    SSN: Optional[str]


@router.get("/V1/user-information/", tags=["user", "information"])
async def get_user_information(
    token: str,
    login: str,
    ID: Optional[int] = None,
    user_id: Optional[int] = None,
    first_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    last_name: Optional[str] = None,
    birthday: Optional[datetime] = None,
    gender: Optional[int] = None,
    location: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    SSN: Optional[str] = None,
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): token of user accessing this content\n
        ID (Optional[int]): ID of entry\n
        user_id (Optional[int]): user id of entry\n
        first_name (Optional[str]): first name of entry\n
        middle_name (Optional[str]): middle name of entry\n
        last_name (Optional[str]): last name of entry\n
        birthday (Optional[datetime]): birthday of entry\n
        gender (Optional[int]): gender of entry\n
        location (Optional[str]): location of entry\n
        timestamp (Optional[datetime]): timestamp of entry\n
        email (Optional[str], optional): email of entry. Defaults to Query(None, min_length=0, max_length=255).\n
        phone (Optional[str], optional): phone number. Defaults to Query(None, min_length=0, max_length=32).\n
        SSN (Optional[str], optional): social security number (For trainer use). Defaults to Query(None, min_length=0, max_length=16).\n
        row_count (Optional[int], optional): row count to be pulled. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): page number to be pulled. Defaults to Query(1, ge=1).\n

    Returns:\n
        json: Json output \n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    table = UserInformation
    sql: Select = select(table)

    if ID is not None:
        sql = sql.where(table.ID == ID)

    if user_id is not None:
        sql = sql.where(table.user_id == user_id)

    if first_name is not None:
        sql = sql.where(table.first_name == first_name)

    if user_id is not None:
        sql = sql.where(table.middle_name == middle_name)

    if last_name is not None:
        sql = sql.where(table.last_name == last_name)

    if birthday is not None:
        sql = sql.where(table.birthday == birthday)

    if gender is not None:
        sql = sql.where(table.gender == gender)

    if location is not None:
        sql = sql.where(table.location == location)

    if timestamp is not None:
        sql = sql.where(table.timestamp == timestamp)

    if email is not None:
        sql = sql.where(table.email == email)

    if phone is not None:
        sql = sql.where(table.phone == phone)

    if SSN is not None:
        sql = sql.where(table.SSN == SSN)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/user-information", tags=["user", "information"])
async def post_user_information(
    login: str, token: str, user_information: user_information
) -> json:
    """
    Args:\n
        user_information (user_information): model of user information and stats\n

    Returns:\n
        json: {"ok": "ok"}\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    values = user_information.dict()
    table = UserInformation
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
