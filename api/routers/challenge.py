import json

from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, status
from api.database.models import (
    Challenge,
    Leaderboard,
    Organization,
    ChallengeDetailsDay,
)
import hashlib
import api.routers.models.challenge as challenge_models
from api.routers.functions.general import get_token_user_id
import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update, insert

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Tokens, TrainerClientHistory, TrainerStats
from api.routers.functions.general import get_token_user_id


router = APIRouter()


@router.get("/v1/challenge/{token}/{challenge_id}", tags=["challenge"])
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


def time_to_string(time):
    return f"{time.year}{time.month}{time.day}{time.hour}{time.minute}{time.second}"


def day_obj_to_string(day):
    start_string = time_to_string(day.start_time)
    end_string = time_to_string(day.end_time)
    return f"{start_string}{end_string}"


def hash_day(day):
    day_string = day_obj_to_string(day)
    return hashlib.sha256(day_string.encode()).hexdigest()


@router.post("/v1/challenge/{token}", tags=["challenge"])
async def start_challenge(
    token: str, challenge_details: challenge_models.challenge_details
) -> json:

    uuid = await get_token_user_id(token=token)

    insert_organization_sql = insert(Organization).values(
        name=challenge_details.organization.name,
        image_route=challenge_details.organization.image_route,
        distance=challenge_details.organization.distance,
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
            await session.execute(insert_organization_sql)
            await session.execute(insert_start_date)
            await session.execute(insert_end_date)

    select_organization_sql = select(Organization).where(
        Organization.name == challenge_details.organization.name
    )
    select_organization_sql = select_organization_sql.where(
        Organization.image_route == challenge_details.organization.image_route
    )
    select_organization_sql = select_organization_sql.where(
        Organization.distance == challenge_details.organization.distance
    )

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
            organization_data = await session.execute(select_organization_sql)
            start_date_data = await session.execute(select_start_date_sql)
            end_date_data = await session.execute(select_end_date_sql)

    leaderboard_result = sqlalchemy_result(leaderboard_data)
    leaderboard_result = leaderboard_result.rows2dict()
    leaderboard_entry_id = leaderboard_result[0].get("ID")

    organization_result = sqlalchemy_result(organization_data)
    organization_result = organization_result.rows2dict()
    organization_entry_id = organization_result[0].get("ID")

    start_result = sqlalchemy_result(start_date_data)
    start_result = start_result.rows2dict()
    start_result_id = start_result[0].get("ID")

    end_result = sqlalchemy_result(end_date_data)
    end_result = end_result.rows2dict()
    end_result_id = end_result[0].get("ID")

    insert_challenge_sql = insert(Challenge).values(
        name=challenge_details.name,
        background=challenge_details.background,
        profile_picture=challenge_details.profile_route,
        description=challenge_details.description,
        start_date=start_result_id,
        end_date=end_result_id,
        distance=challenge_details.distance,
        reward=challenge_details.reward,
        organization=organization_entry_id,
        leaderboard=leaderboard_entry_id,
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
        Challenge.organization == organization_entry_id
    )
    select_challenge_sql = select_challenge_sql.where(
        Challenge.leaderboard == leaderboard_entry_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_challenge_sql)

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


@router.get("/v1/challenge/search/", tags=["challenge"])
async def search_challenge(
    token: str,
    name: str = None,
    description: str = None,
    distance: int = None,
    reward: str = None,
    organization: str = None,
) -> json:

    await get_token_user_id(token=token)

    sql = select(Challenge)

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
    challenge_ids = []
    for challenge in challenge_data:
        challenge_ids.append(challenge.get("id"))

    return HTTPException(status_code=status.HTTP_200_OK, detail=challenge_ids)
