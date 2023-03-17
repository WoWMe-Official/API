import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select, delete, update

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Requests
from api.routers.functions.general import (
    get_token_user_id,
    check_user_block,
    batch_function,
)
from api.routers.v1.profile.profile import get_profile_details

router = APIRouter()


@router.post("/send/{token}/{user_id}", tags=["requests"])
async def send_request(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    if await check_user_block(blocked_id=uuid, blocker_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have been blocked by this user",
        )

    select_requests = select(Requests).where(
        Requests.requesting_user_id == uuid, Requests.requested_user_id == user_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(select_requests)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    if data:
        for d in data:
            if d.get("request_status") == 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user has presently denied your request.",
                )
            if d.get("request_status") == 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You already have a pending request for this user",
                )
            if d.get("request_status") == 2:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user has already accepted your request",
                )

    sql_insert_request = insert(Requests).values(
        requesting_user_id=uuid, requested_user_id=user_id, request_status=1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_insert_request)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="Request has been sent."
    )


@router.delete("/remove/{token}/{user_id}", tags=["requests"])
async def remove_request(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    delete_request = delete(Requests).where(
        Requests.requesting_user_id == uuid,
        Requests.requested_user_id == user_id,
        Requests.request_status == 1,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(delete_request)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Pending request withdrawn."
    )


@router.get("/get-pending/{token}", tags=["requests"])
async def get_pending_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Requests).where(
        Requests.requested_user_id == uuid, Requests.request_status == 1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = list(set([d.get("requesting_user_id") for d in data]))
    try:
        user_ids.remove(uuid)
    except:
        pass
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    combination = list(zip(future_list, data))
    result = []
    for fl, d in combination:
        d["user_information"] = fl
        result.append(d)

    return HTTPException(status_code=status.HTTP_200_OK, detail=result)


@router.get("/get-accepted/{token}", tags=["requests"])
async def get_accepted_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Requests).where(
        Requests.requested_user_id == uuid, Requests.request_status == 2
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = list(set([d.get("requesting_user_id") for d in data]))
    try:
        user_ids.remove(uuid)
    except:
        pass
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    combination = list(zip(future_list, data))
    result = []
    for fl, d in combination:
        d["user_information"] = fl
        result.append(d)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)


@router.get("/get-denied/{token}", tags=["requests"])
async def get_denied_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Requests).where(
        Requests.requested_user_id == uuid, Requests.request_status == 0
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = list(set([d.get("requesting_user_id") for d in data]))
    try:
        user_ids.remove(uuid)
    except:
        pass
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    combination = list(zip(future_list, data))
    result = []
    for fl, d in combination:
        d["user_information"] = fl
        result.append(d)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)


@router.get("/get-all/{token}", tags=["requests"])
async def get_all_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Requests).where(Requests.requested_user_id == uuid)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = list(set([d.get("requesting_user_id") for d in data]))
    try:
        user_ids.remove(uuid)
    except:
        pass
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    combination = list(zip(future_list, data))
    result = []
    for fl, d in combination:
        d["user_information"] = fl
        result.append(d)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)


@router.get("/get-sent-requests/{token}", tags=["requests"])
async def get_sent_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Requests).where(Requests.requesting_user_id == uuid)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    user_ids = list(set([d.get("requesting_user_id") for d in data]))
    try:
        user_ids.remove(uuid)
    except:
        pass
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)

    combination = list(zip(future_list, data))
    result = []
    for fl, d in combination:
        d["user_information"] = fl
        result.append(d)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)


@router.put("/accept-request/{token}", tags=["requests"])
async def accept_a_request(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = (
        update(Requests)
        .where(
            Requests.requesting_user_id == user_id,
            Requests.requested_user_id == uuid,
            Requests.request_status == 1,
        )
        .values(request_status=2)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql)

    return HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Request Accepted"
    )


@router.put("/deny-request/{token}", tags=["requests"])
async def deny_a_request(token: str, user_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = (
        update(Requests)
        .where(
            Requests.requesting_user_id == user_id,
            Requests.requested_user_id == uuid,
            Requests.request_status == 1,
        )
        .values(request_status=0)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql)

    return HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Request Denied")
