from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.config import redis_client
from api.database.functions import generate_token
from api.database.models import Tokens, Blocks
import asyncio
from asyncio import create_task


async def get_token_user_id(token: str):
    sql_select_user_id = select(Tokens).where(Tokens.token == token)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_data = await session.execute(sql_select_user_id)

    uuid_data = sqlalchemy_result(uuid_data)
    uuid_data = uuid_data.rows2dict()

    if len(uuid_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token parameter."
        )

    uuid = uuid_data[0].get("user_id")
    return uuid


async def check_user_block(blocked_id, blocker_id):
    sql_user_block = select(Blocks).where(
        Blocks.blocked_id == blocked_id, Blocks.blocker_id == blocker_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_data = await session.execute(sql_user_block)

    uuid_data = sqlalchemy_result(uuid_data)
    uuid_data = uuid_data.rows2dict()

    if len(uuid_data) == 0:
        return False
    return True


async def image_tokenizer(image_route):
    image_token = await redis_client.get(name=image_route)

    if not image_token:
        image_token = await generate_token(16)
        await redis_client.set(name=image_token, value=image_route, ex=3600)
        await redis_client.set(name=image_route, value=image_token, ex=3600)

    if type(image_token) != str:
        image_token = image_token.decode("utf-8")

    return image_token


async def batch_function(function, data):

    future_list = await asyncio.gather(
        *[create_task(function(d[:][0], d[:][1])) for d in data]
    )
    return future_list
