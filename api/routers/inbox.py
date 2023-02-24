import hashlib
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select, or_

import api.routers.models.event as event_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Event, Inbox, Bcc, Cc, InboxPerms
from api.routers.functions.general import get_token_user_id
from api.routers.models.inbox import inbox, bcc, cc, inbox_conversation_start
from api.database.functions import generate_token
import itertools
import operator

router = APIRouter()


@router.post("/v1/inbox/start/{token}", tags=["inbox"])
async def start_a_new_conversation(
    token: str,
    inbox_conversation_start: inbox_conversation_start,
) -> json:
    """this route allows someone to start a new conversation"""

    uuid = await get_token_user_id(token=token)

    inbox_token = await generate_token()

    sql_inbox = insert(Inbox).values(
        inbox_token=inbox_token,
        sender=uuid,
        subject_line=inbox_conversation_start.subject_line,
        content=inbox_conversation_start.content,
    )

    inbox_perm_list = []
    for u_id in [inbox_conversation_start.sendee, uuid]:
        d = dict()
        d["inbox_token"] = inbox_token
        d["user_id"] = u_id
        d["can_access"] = 1
        inbox_perm_list.append(d)

    sql_inbox_perms = insert(InboxPerms).values(inbox_perm_list)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_inbox)
            await session.execute(sql_inbox_perms)

    return HTTPException(status.HTTP_201_CREATED, detail=inbox_token)


@router.get("/v1/inbox/search/", tags=["inbox"])
async def search_inbox(
    token: str,
    inbox_id: int = None,
    inbox_token: str = None,
    subject_line: str = None,
    content: str = None,
) -> json:
    """this route returns the raw version of given content based upon the requested search parameters."""
    uuid = await get_token_user_id(token=token)

    sql = select(Inbox)
    sql = sql.join(InboxPerms, InboxPerms.inbox_token == Inbox.inbox_token)
    sql = sql.where(InboxPerms.user_id == uuid, InboxPerms.can_access == True)

    if inbox_id:
        sql = sql.where(Inbox.inbox_id == inbox_id)

    if inbox_token:
        sql = sql.where(Inbox.inbox_token == inbox_token)

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

    return HTTPException(status.HTTP_200_OK, detail=inbox_results)


@router.get("/v1/inbox/id-search/", tags=["inbox"])
async def search_inbox_id(
    token: str,
    inbox_id: int = None,
    inbox_token: str = None,
    subject_line: str = None,
    content: str = None,
) -> json:
    """this route returns the ids for the items found in the search, for light-weight searching"""

    uuid = await get_token_user_id(token=token)

    sql = select(Inbox)
    sql = sql.join(InboxPerms, InboxPerms.inbox_token == Inbox.inbox_token)
    sql = sql.where(InboxPerms.user_id == uuid, InboxPerms.can_access == True)

    if inbox_id:
        sql = sql.where(Inbox.inbox_id == inbox_id)

    if inbox_token:
        sql = sql.where(Inbox.inbox_token == inbox_token)

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
        response.append(result.get("inbox_id"))

    return HTTPException(status.HTTP_200_OK, detail=response)


@router.get("/v1/inbox/id-conversations/", tags=["inbox"])
async def get_inbox_conversation_ids(token: str) -> json:
    """
    This route allows you to get the inbox_ids for all active conversations.
    """
    uuid = await get_token_user_id(token=token)
    sql = select(InboxPerms)
    sql = sql.where(InboxPerms.user_id == uuid, InboxPerms.can_access == True)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            inbox_results = await session.execute(sql)

    inbox_results = sqlalchemy_result(inbox_results)
    inbox_results = inbox_results.rows2dict()

    response = list(set([result.get("inbox_token") for result in inbox_results]))

    return HTTPException(status.HTTP_200_OK, detail=response)


@router.get("/v1/inbox/overview/", tags=["inbox"])
async def get_inbox_overview(token: str) -> json:
    """
    Returns an overview of the active conversations and the most recent message in the conversation list. This is ideal for overviews.
    """
    uuid = await get_token_user_id(token=token)
    sql = select(Inbox)
    sql = sql.join(InboxPerms, InboxPerms.inbox_token == Inbox.inbox_token)
    sql = sql.where(InboxPerms.user_id == uuid, InboxPerms.can_access == True)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            inbox_results = await session.execute(sql)

    inbox_results = sqlalchemy_result(inbox_results)
    inbox_results = inbox_results.rows2dict()

    inbox_results.sort(key=operator.itemgetter("inbox_token"))
    groups = itertools.groupby(inbox_results, key=operator.itemgetter("inbox_token"))
    response = dict((cls, list(items)[-1]) for cls, items in groups)

    return HTTPException(status.HTTP_200_OK, detail=response)


@router.post("/v1/inbox/reply/{token}", tags=["inbox"])
async def reply_to_a_conversation(token: str, inbox_token: str, content: str) -> json:
    """
    This route allows you to send a reply to a given inbox token/conversation.
    """
    uuid = await get_token_user_id(token=token)

    sql_inbox = insert(Inbox).values(
        inbox_token=inbox_token,
        sender=uuid,
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
    """
    This route allows you to obtain all up to date inbox information for a user, with all conversations.
    """
    uuid = await get_token_user_id(token=token)

    sql = select(Inbox)
    sql = sql.join(InboxPerms, InboxPerms.inbox_token == Inbox.inbox_token)
    sql = sql.where(InboxPerms.user_id == uuid, InboxPerms.can_access == True)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            inbox_results = await session.execute(sql)

    inbox_results = sqlalchemy_result(inbox_results)
    inbox_results = inbox_results.rows2dict()

    inbox_results.sort(key=operator.itemgetter("inbox_token"))
    groups = itertools.groupby(inbox_results, key=operator.itemgetter("inbox_token"))
    response = dict((cls, list(items)) for cls, items in groups)

    return HTTPException(status.HTTP_200_OK, detail=response)
