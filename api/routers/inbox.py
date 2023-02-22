import hashlib
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select, or_

import api.routers.models.event as event_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Event, Inbox, Bcc, Cc
from api.routers.functions.general import get_token_user_id
from api.routers.models.inbox import inbox, bcc, cc, inbox_conversation_start
from api.database.functions import generate_token

router = APIRouter()


# class inbox(BaseModel):
#     inbox_id: int
#     inbox_token: str
#     timestamp: Optional[datetime.datetime]
#     communication_id: int
#     in_reply_to: Optional[int]
#     bcc: Optional[int]
#     cc: Optional[int]
#     sender: int
#     sendee: int
#     subject_line: str
#     content: str


# class bcc(BaseModel):
#     bcc_id: int
#     inbox_token: str
#     uuid: int


# class cc(BaseModel):
#     bcc_id: int
#     inbox_token: str
#     uuid: int


# class inbox_conversation_start(BaseModel):
#     sendee: int
#     subject_line: str
#     content: str
#     bcc: Optional[list[int]]
#     cc: Optional[list[int]]


@router.post("/v1/inbox/start/{token}", tags=["inbox"])
async def start_a_new_conversation(
    token: str,
    inbox_conversation_start: inbox_conversation_start,
) -> json:
    uuid = await get_token_user_id(token=token)

    inbox_token = await generate_token()

    sql_inbox = insert(Inbox).values(
        inbox_token=inbox_token,
        sender=uuid,
        sendee=inbox_conversation_start.sendee,
        subject_line=inbox_conversation_start.subject_line,
        content=inbox_conversation_start.content,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_inbox)

    return HTTPException(status.HTTP_201_CREATED, detail=inbox_token)


@router.get("/v1/inbox/search/", tags=["inbox"])
async def search_inbox(
    token: str,
    inbox_id: int = None,
    inbox_token: str = None,
    in_reply_to: int = None,
    sender: int = None,
    sendee: int = None,
    subject_line: str = None,
    content: str = None,
) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Inbox)

    if inbox_id:
        sql = sql.where(Inbox.inbox_id == inbox_id)

    if inbox_token:
        sql = sql.where(Inbox.inbox_id == inbox_id)

    if in_reply_to:
        sql = sql.where(Inbox.in_reply_to == in_reply_to)

    if sender:
        sql = sql.where(Inbox.sender == sender)

    if sendee:
        sql = sql.where(Inbox.sendee == sendee)

    if subject_line:
        sql = sql.where(Inbox.subject_line == subject_line)

    if content:
        sql = sql.where(Inbox.content == content)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            inbox_results = await session.execute(sql)

    inbox_results = sqlalchemy_result(inbox_results)
    inbox_results = inbox_results.rows2dict()

    response = []
    for result in inbox_results:
        inbox_sender = result.get("sender")
        inbox_sendee = result.get("sendee")
        if (int(uuid) != inbox_sender) and (int(uuid) != inbox_sendee):
            continue
        response.append(result)

    return HTTPException(status.HTTP_200_OK, detail=response)


@router.post("/v1/inbox/reply/{token}", tags=["inbox"])
async def reply_to_a_conversation(token: str, inbox_token: str, content: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql_inbox = insert(Inbox).values(
        inbox_token=inbox_token,
        sender=uuid,
        sendee=None,
        subject_line=None,
        content=content,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_inbox)

    return HTTPException(status.HTTP_201_CREATED, detail="Message Sent")


@router.get("/v1/inbox/{token}", tags=["inbox"])
async def get_inbox_information(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Inbox)

    sql = sql.where(or_(Inbox.sendee == uuid, Inbox.sender == uuid))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            inbox_results = await session.execute(sql)

    inbox_results = sqlalchemy_result(inbox_results)
    inbox_results = inbox_results.rows2dict()

    return HTTPException(status.HTTP_200_OK, detail=inbox_results)
