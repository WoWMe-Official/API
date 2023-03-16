import hashlib
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select, delete, update

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Event, Favorites
from api.routers.functions.general import (
    get_token_user_id,
    check_user_block,
    batch_function,
)
from api.routers.v1.profile.profile import get_profile_details

router = APIRouter()


@router.post("/add/{token}/{user_id}", tags=["favorites"])
async def add_favorite(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    if await check_user_block(blocked_id=uuid, blocker_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have been blocked by this user",
        )
    # lowest number user id goes in the left field (user_id_1)
    if int(uuid) < int(user_id):
        select_favorites = select(Favorites).where(Favorites.user_id_1 == uuid)
    else:
        select_favorites = select(Favorites).where(Favorites.user_id_2 == uuid)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(select_favorites)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    paired_ids = []
    for d in data:
        paired_ids.append(d.get("user_id_1"))
        paired_ids.append(d.get("user_id_2"))

    paired_ids = list(set(paired_ids))

    if user_id in paired_ids:
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail="This user has already been added to the favorite list",
        )

    if int(uuid) < int(user_id):
        sql_insert_favorites = insert(Favorites).values(
            user_id_1=uuid, user_id_2=user_id
        )
    else:
        sql_insert_favorites = insert(Favorites).values(
            user_id_1=user_id, user_id_2=uuid
        )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_insert_favorites)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="User has been added to favorites."
    )


@router.delete("/remove/{token}/{user_id}", tags=["favorites"])
async def remove_favorite(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    if int(uuid) < int(user_id):
        delete_favorites = delete(Favorites).where(
            Favorites.user_id_1 == uuid, Favorites.user_id_2 == user_id
        )
    else:
        delete_favorites = delete(Favorites).where(
            Favorites.user_id_2 == uuid, Favorites.user_id_1 == user_id
        )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(delete_favorites)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Favorite removed."
    )


@router.get("/get/{token}", tags=["favorites"])
async def get_favorites(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Favorites).where(
        or_(Favorites.user_id_1 == uuid, Favorites.user_id_2 == uuid)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = []
    for d in data:
        user_ids.append(d.get("user_id_1"))
        user_ids.append(d.get("user_id_2"))
    user_ids = list(set(user_ids))
    user_ids.remove(uuid)

    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)
