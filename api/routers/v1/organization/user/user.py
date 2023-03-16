import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete, insert, select, update

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import (
    OrganizationMembers,
)
from api.routers.functions.general import (
    batch_function,
    get_token_user_id,
    check_user_block,
)
from api.routers.v1.profile.profile import get_profile_details

router = APIRouter()


@router.post("/invite/{token}/{user_id}/{organization_id}", tags=["organization"])
async def invite_user_to_organization(
    token: str, user_id: int, organization_id: int
) -> json:
    uuid = await get_token_user_id(token=token)

    if await check_user_block(blocked_id=uuid, blocker_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have been blocked from contacting this user.",
        )

    uuid_permission = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        or_(
            OrganizationMembers.user_org_admin == 1,
            OrganizationMembers.user_org_owner == 1,
        ),
        OrganizationMembers.organization_id == organization_id,
    )
    pending_request_check = select(OrganizationMembers).where(
        OrganizationMembers.organization_id == organization_id,
        or_(
            OrganizationMembers.request_status == 0,
            OrganizationMembers.request_status == 2,
        ),
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_permission = await session.execute(uuid_permission)
            user_id_request_pending = await session.execute(pending_request_check)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to invite this user.",
        )

    user_id_request_pending = sqlalchemy_result(user_id_request_pending)
    user_id_request_pending = user_id_request_pending.rows2dict()

    if user_id_request_pending:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user has a pending request to this organization.",
        )

    send_invite_to_user = insert(OrganizationMembers).values(
        organization_id=organization_id,
        user_id=user_id,
        user_org_admin=0,
        user_org_owner=0,
        recruiter=uuid,
        request_status=1,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(send_invite_to_user)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="The user has been invited to join the organization.",
    )


@router.delete("/remove/{token}/{user_id}", tags=["organization"])
async def remove_user_from_organization(
    token: str, user_id: int, organization_id: int
) -> json:
    uuid = await get_token_user_id(token=token)

    uuid_permission = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        or_(
            OrganizationMembers.user_org_admin == 1,
            OrganizationMembers.user_org_owner == 1,
        ),
        OrganizationMembers.organization_id == organization_id,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_permission = await session.execute(uuid_permission)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to remove this user.",
        )

    remove_sql = delete(OrganizationMembers).where(
        OrganizationMembers.organization_id == organization_id,
        OrganizationMembers.user_id == user_id,
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(remove_sql)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User has been removed from the organization.",
    )


@router.get("/get/{token}", tags=["organization"])
async def get_organization_users(token: str, organization_id: int) -> json:
    await get_token_user_id(token=token)
    sql = select(OrganizationMembers).where(
        OrganizationMembers.organization_id == organization_id,
        or_(
            OrganizationMembers.request_status == 2,
            OrganizationMembers.user_org_admin == 1,
            OrganizationMembers.user_org_owner == 1,
        ),
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            members_result = await session.execute(sql)

    members_result = sqlalchemy_result(members_result)
    members_result = members_result.rows2dict()
    user_ids = [m.get("user_id") for m in members_result]
    data_pack = [tuple((token, u_id)) for u_id in user_ids]
    future_list = await batch_function(get_profile_details, data=data_pack)
    r = list(zip(members_result, future_list))
    response = []
    for k, v in r:
        k["user_information"] = v
        response.append(k)
    return HTTPException(status_code=status.HTTP_200_OK, detail=response)


@router.put("/promote-admin/{token}/{user_id}/{organization_id}", tags=["organization"])
async def promote_user_to_admin(token: str, user_id: int, organization_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    uuid_permission = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.user_org_owner == 1,
        OrganizationMembers.organization_id == organization_id,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_permission = await session.execute(uuid_permission)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to promote this user.",
        )

    sql_update = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.organization_id == organization_id,
            OrganizationMembers.user_id == user_id,
        )
        .values(user_org_admin=1)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User has been promoted to admin of the organization.",
    )


@router.put("/demote-admin/{token}", tags=["organization"])
async def demote_user_from_admin(
    token: str, user_id: int, organization_id: int
) -> json:
    uuid = await get_token_user_id(token=token)

    uuid_permission = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.user_org_owner == 1,
        OrganizationMembers.organization_id == organization_id,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_permission = await session.execute(uuid_permission)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to demote this user.",
        )

    sql_update = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.organization_id == organization_id,
            OrganizationMembers.user_id == user_id,
        )
        .values(user_org_admin=0)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="User has been demoted.",
    )


@router.put("/transfer-ownership/{token}", tags=["organization"])
async def transfer_ownership_to_another_user(
    token: str, user_id: int, organization_id: int
) -> json:
    uuid = await get_token_user_id(token=token)

    uuid_permission = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.user_org_owner == 1,
        OrganizationMembers.organization_id == organization_id,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            uuid_permission = await session.execute(uuid_permission)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permissions to transfer ownership this user.",
        )

    sql_update_ownership_add = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.organization_id == organization_id,
            OrganizationMembers.user_id == user_id,
        )
        .values(user_org_owner=1)
    )
    sql_update_ownership_remove = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.organization_id == organization_id,
            OrganizationMembers.user_id == uuid,
        )
        .values(user_org_owner=0)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update_ownership_add)
            await session.execute(sql_update_ownership_remove)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Ownership has been transfered.",
    )


@router.get("/get-requests/{token}", tags=["organization"])
async def get_pending_join_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid, OrganizationMembers.request_status == 1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    raise HTTPException(status_code=status.HTTP_200_OK, detail=result)


@router.put("/accept-request/{token}", tags=["organization"])
async def accept_pending_join_request(token: str, organization_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.organization_id == organization_id,
        OrganizationMembers.request_status == 1,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have a pending result for this organization.",
        )

    update_request = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.user_id == uuid,
            OrganizationMembers.organization_id == organization_id,
        )
        .values(request_status=2)
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Accepted request."
    )


@router.put("/deny-request/{token}", tags=["organization"])
async def deny_pending_join_request(token: str, organization_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.organization_id == organization_id,
        OrganizationMembers.request_status == 1,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have a pending result for this organization.",
        )

    update_request = (
        update(OrganizationMembers)
        .where(
            OrganizationMembers.user_id == uuid,
            OrganizationMembers.organization_id == organization_id,
        )
        .values(request_status=0)
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Denied request")
