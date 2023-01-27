from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Tokens, Blocks


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
