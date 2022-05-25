from datetime import datetime
import json
from typing import Optional
from urllib.request import Request

from pyparsing import Opt

from api.database.functions import (
    USERDATA_ENGINE,
    EngineType,
    sqlalchemy_result,
    verify_token,
)
from api.database.models import UserChat
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from pydantic.fields import Field
from pymysql import Timestamp
from sqlalchemy import BIGINT, DATETIME, TIMESTAMP, BigInteger, func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, select, insert

router = APIRouter()


class user_chat(BaseModel):
    """
    User chat base model containing the types and content expected by the database
    """

    ID: Optional[int]
    timestamp: Optional[datetime]
    s_user_id: Optional[int]
    r_user_id: Optional[int]
    contains_image: Optional[int]
    image_key: Optional[str]
    chat: Optional[str]


@router.get("/V1/user-chat/", tags=["user", "chat"])
async def get_user_chat(
    token: str,
    login: str,
    ID: Optional[int] = None,
    timestamp: Optional[datetime] = None,
    s_user_id: Optional[int] = None,
    r_user_id: Optional[int] = None,
    contains_image: Optional[int] = None,
    image_key: Optional[str] = None,
    chat: Optional[str] = Query(None, max_length=280),
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): token of the accessing user\n
        ID (int): chat entry information\n
        timestamp (_type_, optional): chat timestamp. Defaults to Optional[datetime].\n
        s_user_id (_type_, optional): sending user id. Defaults to Optional[int].\n
        r_user_id (_type_, optional): receiving user id. Defaults to Optional[int].\n
        contains_image (_type_, optional): if the chat contains an image. Defaults to Optional[int].\n
        image_key (_type_, optional): image reference key. Defaults to Optional[int].\n
        chat (_type_, optional): chat content. Defaults to Query(None, max_length=255).\n
        row_count (Optional[int], optional): how many rows should be pulled with this request. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): how many pages should be pulled with this request. Defaults to Query(1, ge=1).\n

    Returns:\n
        json: Json of above query\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    table = UserChat
    sql: Select = select(table)

    if not s_user_id == None:
        sql = sql.where(table.s_user_id == s_user_id)

    if not r_user_id == None:
        sql = sql.where(table.r_user_id == r_user_id)

    if not timestamp == None:
        sql = sql.where(table.timestamp == timestamp)

    if not contains_image == None:
        sql = sql.where(table.contains_image == contains_image)

    if not image_key == None:
        sql = sql.where(table.image_key == image_key)

    if not chat == None:
        sql = sql.where(table.chat == chat)

    if not ID == None:
        sql = sql.where(table.ID == ID)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/V1/user-chat", tags=["user", "chat"])
async def post_user_chat(login: str, token: str, user_chat: user_chat) -> json:
    """
    Args:\n
        user_chat (user_chat): user chat model\n
    Returns:\n
        json: {"ok": "ok"}\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    values = user_chat.dict()
    table = UserChat
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
