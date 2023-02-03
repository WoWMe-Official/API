import hashlib
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

import api.routers.models.event as event_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Event
from api.routers.functions.general import get_token_user_id

router = APIRouter()


def hash(string):
    return hashlib.sha256(string.encode()).hexdigest()


@router.post("/v1/events/{token}", tags=["event"])
async def post_event_information(token: str, event: event_models.event) -> json:
    event.uuid = await get_token_user_id(token=token)
    event.hash = hash(
        f"{event.background_image}_{event.uuid}_{event.title}_{event.num_excercises}_{event.difficulty}"
    )

    insert_event = insert(Event).values(event.dict())
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_event)

    raise HTTPException(status_code=status.HTTP_201_CREATED, detail=f"{event.hash}")


@router.get("/v1/events/{token}", tags=["event"])
async def get_event_information(token: str, event_hash: str) -> json:
    uuid = await get_token_user_id(token=token)

    select_event = select(Event).where(Event.hash == event_hash)
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            event_result = await session.execute(select_event)

    event_result = sqlalchemy_result(event_result)
    event_result = event_result.rows2dict()
    raise HTTPException(status_code=status.HTTP_200_OK, detail=event_result)


@router.get("/v1/events/search/", tags=["event"])
async def search_events(
    token: str,
    event_hash: str = None,
    title: str = None,
    description: str = None,
    num_excercises: int = None,
    min_num_excercises: int = None,
    max_num_excercises: int = None,
    difficulty: str = None,
) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Event)

    if event_hash:
        sql = sql.where(Event.hash == event_hash)

    if title:
        sql = sql.where(Event.title == title)

    if description:
        sql = sql.where(Event.description == description)

    if num_excercises and (not max_num_excercises or not min_num_excercises):
        sql = sql.where(Event.num_excercises == num_excercises)

    if max_num_excercises and not num_excercises:
        sql = sql.where(Event.num_excercises <= max_num_excercises)

    if min_num_excercises and not num_excercises:
        sql = sql.where(Event.num_excercises >= min_num_excercises)

    if difficulty:
        sql = sql.where(Event.difficulty == difficulty)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            event_result = await session.execute(sql)

    event_result = sqlalchemy_result(event_result)
    event_result = event_result.rows2dict()

    event_hashes = []
    for event in event_result:
        event_hashes.append(event.get("hash"))
    raise HTTPException(status_code=status.HTTP_200_OK, detail=event_hashes)
