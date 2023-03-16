import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete, insert, select, update

import api.routers.models.challenge as challenge_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import (
    Challenge,
    ChallengeDetailsDay,
    Leaderboard,
    Organization,
    OrganizationMembers,
)
from api.routers.functions.general import batch_function, get_token_user_id, hash_day
from api.routers.v1.profile.profile import get_profile_details
from api.routers.v1.organization.user.user import get_organization_users

router = APIRouter()


@router.post("/create/{token}", tags=["organization"])
async def create_organization(
    token: str, organization_details: challenge_models.organization
) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Organization).where(Organization.name == organization_details.name)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An organization by this name currently exists.",
        )

    sql_insert = insert(Organization).values(
        name=organization_details.name,
        image_route=organization_details.image_route,
        distance=organization_details.distance,
    )

    sql_select = select(Organization).where(
        Organization.name == organization_details.name
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_insert)
            select_result = await session.execute(sql_select)

    select_result = sqlalchemy_result(select_result)
    select_result = select_result.rows2dict()

    if not select_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured attempting to create your organization, please try again later.",
        )

    organization_id = None
    for r in select_result:
        if r.get("name") == organization_details.name:
            organization_id = r.get("ID")

    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error with this route, please try again later.",
        )

    insert_organization_member = insert(OrganizationMembers).values(
        user_id=uuid,
        organization_id=organization_id,
        user_org_admin=1,
        user_org_owner=1,
        request_status=2,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_organization_member)

    return HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your organization has been created.",
    )


@router.delete("/delete/{token}", tags=["organization"])
async def delete_organization(token: str, organization_id: int) -> json:
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

    result = sqlalchemy_result(uuid_permission)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this organization.",
        )

    sql_delete_organization = delete(Organization).where(
        Organization.ID == organization_id
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_delete_organization)

    return HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="The organization has been deleted.",
    )


@router.put("/update/{token}", tags=["organization"])
async def update_organization(
    token: str,
    organization_id: int,
    organization_details: challenge_models.organization,
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

    result = sqlalchemy_result(uuid_permission)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this organization",
        )

    sql_update = update(Organization).where(Organization.ID == organization_id)

    if organization_details.name:
        sql_update = sql_update.values(name=organization_details.name)
    if organization_details.distance:
        sql_update = sql_update.values(distance=organization_details.distance)
    if organization_details.image_route:
        sql_update = sql_update.values(image_route=organization_details.image_route)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update)
    return HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="Organization information modified.",
    )


@router.get("/overview/{token}", tags=["organization"])
async def get_organization_details(token: str, organization_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    select_organization_details = select(Organization).where(
        Organization.ID == organization_id
    )
    select_organization_members = select(OrganizationMembers).where(
        OrganizationMembers.organization_id == organization_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            org_details = await session.execute(select_organization_details)
            organization_members = await session.execute(select_organization_members)

    org_details = sqlalchemy_result(org_details)
    org_details = org_details.rows2dict()

    organization_members = sqlalchemy_result(organization_members)
    organization_members = organization_members.rows2dict()

    if not org_details:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Information about this organization is missing, or this organization does not exist.",
        )

    org_details = org_details[0]
    org_details["member_count"] = len(organization_members)

    return HTTPException(status_code=status.HTTP_200_OK, detail=org_details)


@router.get("/search/{token}", tags=["organization"])
async def search_organizations(
    token: str, organization_id: str = None, organization_name: str = None
) -> json:
    await get_token_user_id(token=token)

    sql = select(Organization)
    if organization_id:
        sql = sql.where(Organization.ID == organization_id)
    if organization_name:
        sql = sql.where(Organization.name == organization_name)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No organizations found."
        )

    organization_ids = [r.get("ID") for r in result]
    data_pack = [tuple((token, u_id)) for u_id in organization_ids]
    future_list = await batch_function(get_organization_details, data=data_pack)
    response = []
    for d in future_list:
        if d.status_code == 200:
            response.append(d.detail)
    raise HTTPException(status_code=status.HTTP_200_OK, detail=response)
