import json

from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, status
from api.database.models import (
    Challenge,
    Leaderboard,
    Organization,
    ChallengeDetailsDay,
)
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
    """
    Get Challenge Details
    Params:
    {
    Challenge id: number,
    Token: string,
    }

    Returns:
    {
    Name: string,
    Background: string,
    Profile picture: string,
    Description: string,
    Start date: string,
    End date: string,
    Distance: number,
    Reward: string,
    Organization: { name: string, image: string, distance: number}
    Leaderboard: array: {name: string, pace: number, distance: number}
    }
    """


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

    insert_start_date = insert(ChallengeDetailsDay).values(
        day_id=challenge_details.start_date.day,
        start_time=challenge_details.start_date.start_time,
        end_time=challenge_details.start_date.end_time,
        is_start=1,
    )

    insert_end_date = insert(ChallengeDetailsDay).values(
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
        ChallengeDetailsDay.day_id == challenge_details.start_date.day
    )
    select_start_date_sql = select_start_date_sql.where(
        ChallengeDetailsDay.start_time == challenge_details.start_date.start_time
    )
    select_start_date_sql = select_start_date_sql.where(
        ChallengeDetailsDay.end_time == challenge_details.start_date.end_time
    )
    select_start_date_sql = select_start_date_sql.where(
        ChallengeDetailsDay.is_start == 1
    )

    select_end_date_sql = select(ChallengeDetailsDay).where(
        ChallengeDetailsDay.day_id == challenge_details.end_date.day
    )
    select_end_date_sql = select_end_date_sql.where(
        ChallengeDetailsDay.start_time == challenge_details.end_date.start_time
    )
    select_end_date_sql = select_end_date_sql.where(
        ChallengeDetailsDay.end_time == challenge_details.end_date.end_time
    )
    select_end_date_sql = select_end_date_sql.where(
        ChallengeDetailsDay.is_start == False
    )

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
            challenge_data = await session.execute(select_challenge_sql)

    challenge_result = sqlalchemy_result(challenge_data)
    challenge_result = challenge_result.rows2dict()
    challenge_result_id = challenge_result[0].get("ID")

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail=f"{challenge_result_id}"
    )
