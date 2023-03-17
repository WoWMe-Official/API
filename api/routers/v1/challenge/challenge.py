import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import delete, insert, select, update


import api.routers.models.challenge as challenge_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import (
    Challenge,
    ChallengeDetailsDay,
    OrganizationMembers,
    ChallengeMembers,
    Leaderboard,
    Organization,
)
from api.routers.functions.general import (
    batch_function,
    get_token_user_id,
    hash_day,
    check_user_block,
)

router = APIRouter()


@router.get("/get/{token}/{challenge_id}", tags=["challenge"])
async def get_challenge_details(token: str, challenge_id: str) -> json:

    uuid = await get_token_user_id(token=token)

    select_challenge_sql = select(Challenge).where(Challenge.id == challenge_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            challenge_data = await session.execute(select_challenge_sql)

    challenge_result = sqlalchemy_result(challenge_data)
    challenge_result = challenge_result.rows2dict()

    start_id = challenge_result[0].get("start_date")
    end_id = challenge_result[0].get("end_date")
    organization_id = challenge_result[0].get("organization")
    leaderboard_id = challenge_result[0].get("leaderboard")

    sql_start = select(ChallengeDetailsDay).where(ChallengeDetailsDay.ID == start_id)
    sql_end = select(ChallengeDetailsDay).where(ChallengeDetailsDay.ID == end_id)
    sql_organization = select(Organization).where(Organization.ID == organization_id)
    sql_leaderboard = select(Organization).where(Leaderboard.ID == leaderboard_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            start_data = await session.execute(sql_start)
            end_data = await session.execute(sql_end)
            organization_data = await session.execute(sql_organization)
            leaderboard_data = await session.execute(sql_leaderboard)

    start_result = sqlalchemy_result(start_data)
    end_result = sqlalchemy_result(end_data)
    organization_result = sqlalchemy_result(organization_data)
    leaderboard_result = sqlalchemy_result(leaderboard_data)

    start_result = start_result.rows2dict()
    end_result = end_result.rows2dict()
    organization_result = organization_result.rows2dict()
    leaderboard_result = leaderboard_result.rows2dict()

    challenge_result[0]["start_date"] = start_result[0]
    challenge_result[0]["end_date"] = end_result[0]
    challenge_result[0]["organization"] = organization_result[0]
    challenge_result[0]["leaderboard"] = leaderboard_result[0]

    return HTTPException(status_code=status.HTTP_200_OK, detail=challenge_result)


@router.post("/start/{token}", tags=["challenge"])
async def start_challenge(
    token: str, challenge_details: challenge_models.challenge_details
) -> json:
    uuid = await get_token_user_id(token=token)
    challenge_details.user_id = uuid

    select_organization_sql = select(OrganizationMembers).where(
        OrganizationMembers.user_id == uuid,
        OrganizationMembers.organization_id == challenge_details.organization,
        or_(
            OrganizationMembers.user_org_admin == 1,
            OrganizationMembers.user_org_owner == 1,
        ),
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            organization_result = await session.execute(select_organization_sql)

    organization_result = sqlalchemy_result(organization_result)
    organization_result = organization_result.rows2dict()
    if not organization_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not an admin or owner of the given organization, or the organization does not exist.",
        )

    insert_leaderboard_sql = insert(Leaderboard).values(
        name=challenge_details.leaderboard.name,
        distance=challenge_details.leaderboard.distance,
        pace=challenge_details.leaderboard.pace,
    )

    start_hash = hash_day(challenge_details.start_date)
    end_hash = hash_day(challenge_details.end_date)

    insert_start_date = insert(ChallengeDetailsDay).values(
        day_hash=start_hash,
        day_id=challenge_details.start_date.day,
        start_time=challenge_details.start_date.start_time,
        end_time=challenge_details.start_date.end_time,
        is_start=1,
    )

    insert_end_date = insert(ChallengeDetailsDay).values(
        day_hash=end_hash,
        day_id=challenge_details.end_date.day,
        start_time=challenge_details.end_date.start_time,
        end_time=challenge_details.end_date.end_time,
        is_start=0,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_leaderboard_sql)
            await session.execute(insert_start_date)
            await session.execute(insert_end_date)

    select_leaderboard_sql = select(Leaderboard).where(
        Leaderboard.name == challenge_details.leaderboard.name
    )
    select_leaderboard_sql = select_leaderboard_sql.where(
        Leaderboard.distance == challenge_details.leaderboard.distance
    )
    select_leaderboard_sql = select_leaderboard_sql.where(
        Leaderboard.pace == challenge_details.leaderboard.pace
    )

    select_start_date_sql = select(ChallengeDetailsDay).where(
        ChallengeDetailsDay.day_hash == start_hash
    )
    select_start_date_sql = select_start_date_sql.where(
        ChallengeDetailsDay.is_start == 1
    )

    select_end_date_sql = select(ChallengeDetailsDay).where(
        ChallengeDetailsDay.day_hash == end_hash
    )
    select_end_date_sql = select_end_date_sql.where(ChallengeDetailsDay.is_start == 0)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            leaderboard_data = await session.execute(select_leaderboard_sql)
            start_date_data = await session.execute(select_start_date_sql)
            end_date_data = await session.execute(select_end_date_sql)

    leaderboard_result = sqlalchemy_result(leaderboard_data)
    leaderboard_result = leaderboard_result.rows2dict()
    leaderboard_entry_id = leaderboard_result[0].get("ID")

    start_result = sqlalchemy_result(start_date_data)
    start_result = start_result.rows2dict()
    start_result_id = start_result[0].get("ID")

    end_result = sqlalchemy_result(end_date_data)
    end_result = end_result.rows2dict()
    end_result_id = end_result[0].get("ID")

    insert_challenge_sql = insert(Challenge).values(
        name=challenge_details.name,
        user_id=challenge_details.user_id,
        background=challenge_details.background,
        profile_picture=challenge_details.profile_route,
        description=challenge_details.description,
        start_date=start_result_id,
        end_date=end_result_id,
        distance=challenge_details.distance,
        reward=challenge_details.reward,
        organization=challenge_details.organization,
        leaderboard=leaderboard_entry_id,
    )

    select_challenge_sql = select(Challenge).where(
        Challenge.user_id == challenge_details.user_id
    )
    select_challenge_sql = select(Challenge).where(
        Challenge.name == challenge_details.name
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.background == challenge_details.background
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.profile_picture == challenge_details.profile_route
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.description == challenge_details.description
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.start_date == start_result_id
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.end_date == end_result_id
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.distance == challenge_details.distance
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.reward == challenge_details.reward
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.organization == challenge_details.organization
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.leaderboard == leaderboard_entry_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_challenge_sql)
            challenge_data = await session.execute(select_challenge_sql)

    challenge_result = sqlalchemy_result(challenge_data)
    challenge_result = challenge_result.rows2dict()
    challenge_result_id = challenge_result[0].get("id")

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail=f"{challenge_result_id}"
    )


@router.put("/edit/{token}", tags=["challenge"])
async def edit_challenge_details(
    token: str,
    challenge_id: int,
    challenge_details: challenge_models.edit_challenge_details,
) -> json:
    uuid = await get_token_user_id(token=token)

    sql = sql.update(Challenge).where(
        Challenge.id == challenge_id, Challenge.user_id == uuid
    )
    challenge_details_dict = dict()
    if challenge_details.edit_name:
        challenge_details_dict["name"] = challenge_details.edit_name
    if challenge_details.edit_end_date:
        challenge_details_dict["end_date"] = challenge_details.edit_end_date
    if challenge_details.edit_background:
        challenge_details_dict["background"] = challenge_details.edit_background
    if challenge_details.edit_start_date:
        challenge_details_dict["start_date"] = challenge_details.edit_start_date
    if challenge_details.edit_reward:
        challenge_details_dict["reward"] = challenge_details.edit_reward
    if challenge_details.edit_profile_route:
        challenge_details_dict["profile_route"] = challenge_details.edit_profile_route

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail=f"Challenge Information Updated"
    )


@router.delete("/delete/{token}", tags=["challenge"])
async def delete_challenge(token: str, challenge_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = delete(Challenge).where(
        Challenge.user_id == uuid, Challenge.id == challenge_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Challenge deleted."
    )


@router.get("/search/", tags=["challenge"])
async def search_challenge(
    token: str,
    name: str = None,
    user_id: str = None,
    description: str = None,
    distance: int = None,
    reward: str = None,
    organization: str = None,
) -> json:

    await get_token_user_id(token=token)

    sql = select(Challenge)

    if user_id:
        sql = sql.where(Challenge.user_id == user_id)

    if name:
        sql = sql.where(Challenge.name == name)

    if description:
        sql = sql.where(Challenge.description == name)

    if distance:
        sql = sql.where(Challenge.distance == distance)

    if reward:
        sql = sql.where(Challenge.reward == reward)

    if organization:
        organization_sql = sql.where(Organization.name == organization)

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                organization_data = await session.execute(organization_sql)
                organization_data = sqlalchemy_result(organization_data)
                organization_data = organization_data.rows2dict()
                organization_id = organization_data[0].get("id")
        sql = sql.where(Challenge.organization == organization_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            challenge_data = await session.execute(sql)

    challenge_data = sqlalchemy_result(challenge_data)
    challenge_data = challenge_data.rows2dict()
    challenge_ids = [challenge.get("id") for challenge in challenge_data]
    data_pack = [tuple((token, challenge_id)) for challenge_id in challenge_ids]

    future_list = await batch_function(get_challenge_details, data=data_pack)

    return HTTPException(status_code=status.HTTP_200_OK, detail=future_list)


@router.post("/request-join/{token}/{challenge_id}", tags=["challenge"])
async def request_to_join_challenge(token: str, challenge_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(ChallengeMembers).where(
        ChallengeMembers.challenge_id == challenge_id, ChallengeMembers.user_id == uuid
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user already has a request to join the challenge.",
        )

    insert_request = insert(ChallengeMembers).values(
        user_id=uuid, recruiter=uuid, challenge_id=challenge_id, request_status=1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(insert_request)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="You have requested to join this challenge.",
    )


@router.post("/invite/{token}/{user_id}/{challenge_id}", tags=["challenge"])
async def invite_to_challenge(token: str, user_id: int, challenge_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    if await check_user_block(blocked_id=uuid, blocker_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have been blocked by this user, and cannot send them challenge requests.",
        )

    sql = select(ChallengeMembers).where(
        ChallengeMembers.challenge_id == challenge_id,
        ChallengeMembers.user_id == user_id,
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    if result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user already has a request to join the challenge.",
        )

    insert_request = insert(ChallengeMembers).values(
        user_id=user_id, recruiter=uuid, challenge_id=challenge_id, request_status=1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(insert_request)
    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="You have sent this user a request to join a challenge.",
    )


@router.put("/accept-request/{token}/{user_id}/{challenge_id}", tags=["challenge"])
async def accept_challenge_request(token: str, user_id: int, challenge_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    get_challenge_request_id = select(ChallengeMembers).where(
        ChallengeMembers.challenge_id == challenge_id,
        ChallengeMembers.user_id == user_id,
        ChallengeMembers.request_status == 1,
    )
    get_challenge_information = select(Challenge).where(Challenge.id == challenge_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(get_challenge_request_id)
            challenge_information_result = await session.execute(
                get_challenge_information
            )

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    challenge_information_result = sqlalchemy_result(challenge_information_result)
    challenge_information_result = challenge_information_result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user does not have a request for this challenge",
        )

    if not challenge_information_result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This challenge does not exist or could not be found.",
        )

    recruiter = result[0].get("recruiter")

    validation = None
    if (recruiter == user_id) & (uuid != user_id):
        # validate self
        validation = uuid
    elif (recruiter != user_id) & (uuid == user_id):
        # validate recruiter
        validation = recruiter
    elif int(recruiter) == int(uuid) == int(user_id):
        # attempt to join on self
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="You cannot accept your own request to join a challenge...",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="You cannot accept this challenge request for another reason.",
        )

    organization_id = [
        challenge.get("organization") for challenge in challenge_information_result
    ][0]

    select_validation = select(OrganizationMembers).where(
        OrganizationMembers.organization_id == organization_id,
        OrganizationMembers.user_id == validation,
        or_(
            OrganizationMembers.user_org_admin == 1,
            OrganizationMembers.user_org_owner == 1,
        ),
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            select_validation_result = await session.execute(select_validation)

    select_validation_result = sqlalchemy_result(select_validation_result)
    select_validation_result = select_validation_result.rows2dict()

    if not select_validation_result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This challenge request cannot be accepted as it has now become invalid, please try again.",
        )

    sql_update = (
        update(ChallengeMembers)
        .where(
            ChallengeMembers.challenge_id == challenge_id,
            ChallengeMembers.user_id == user_id,
        )
        .values(request_status=2)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update)

    return HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="Challenge accepted.",
    )


@router.put(
    "/deny-request-challenge/{token}/{user_id}/{challenge_id}", tags=["challenge"]
)
async def deny_challenge_request(token: str, user_id: int, challenge_id: int) -> json:
    uuid = await get_token_user_id(token=token)

    get_challenge_request_id = select(ChallengeMembers).where(
        ChallengeMembers.challenge_id == challenge_id,
        ChallengeMembers.user_id == user_id,
        ChallengeMembers.request_status == 1,
    )
    get_challenge_information = select(Challenge).where(Challenge.id == challenge_id)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(get_challenge_request_id)
            challenge_information_result = await session.execute(
                get_challenge_information
            )

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    challenge_information_result = sqlalchemy_result(challenge_information_result)
    challenge_information_result = challenge_information_result.rows2dict()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user does not have a request for this challenge",
        )

    if not challenge_information_result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This challenge does not exist or could not be found.",
        )

    recruiter = result[0].get("recruiter")

    validation = None
    if (recruiter == user_id) & (uuid != user_id):
        validation = uuid

        organization_id = [
            challenge.get("organization") for challenge in challenge_information_result
        ][0]

        select_validation = select(OrganizationMembers).where(
            OrganizationMembers.organization_id == organization_id,
            OrganizationMembers.user_id == validation,
            or_(
                OrganizationMembers.user_org_admin == 1,
                OrganizationMembers.user_org_owner == 1,
            ),
        )

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                select_validation_result = await session.execute(select_validation)

        select_validation_result = sqlalchemy_result(select_validation_result)
        select_validation_result = select_validation_result.rows2dict()

        if not select_validation_result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This challenge request cannot be accepted as it has now become invalid, please try again.",
            )
    elif uuid == user_id:
        pass
        # you dont need to validate anything here just deny the request
    else:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="You cannot deny this challenge request for another reason.",
        )

    sql_update = (
        update(ChallengeMembers)
        .where(
            ChallengeMembers.challenge_id == challenge_id,
            ChallengeMembers.user_id == user_id,
        )
        .values(request_status=0)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_update)

    return HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="Challenge denied.",
    )


@router.get("/get-requests/{token}", tags=["challenge"])
async def get_active_challenge_requests(token: str) -> json:
    uuid = await get_token_user_id(token=token)

    select_active_challenges = select(ChallengeMembers).where(
        ChallengeMembers.user_id == uuid, ChallengeMembers.request_status == 1
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            challenge_requests = await session.execute(select_active_challenges)

    challenge_requests = sqlalchemy_result(challenge_requests)
    challenge_requests = challenge_requests.rows2dict()

    raise HTTPException(status_code=status.HTTP_200_OK, detail=challenge_requests)
