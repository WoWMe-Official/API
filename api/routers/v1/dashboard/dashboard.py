import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update

from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import Tokens, TrainerClientHistory, TrainerStats
from api.routers.functions.general import get_token_user_id

router = APIRouter()


@router.get("/{token}", tags=["dashboard"])
async def get_dashboard_information(token: str) -> json:
    """
    This code defines a route for getting dashboard information for a trainer. The function takes a token as input, which is used to retrieve the trainer ID. Then, two SQL queries are executed to retrieve the trainer's stats and client history. The results are processed and used to create a response JSON object with information on the trainer's earnings, taxes, hours worked, sessions worked, categories assigned, client count, client profiles, steps, and distance. The response is then returned.
    """

    uuid = await get_token_user_id(token=token)

    sql_select_trainer_stats = select(TrainerStats).where(
        TrainerStats.trainer_id == uuid
    )
    sql_select_trainer_client_history = select(TrainerClientHistory).where(
        TrainerClientHistory.trainer_id == uuid
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            trainer_stats_data = await session.execute(sql_select_trainer_stats)
            trainer_client_data = await session.execute(
                sql_select_trainer_client_history
            )

    trainer_stats_data = sqlalchemy_result(trainer_stats_data)
    trainer_stats_data = trainer_stats_data.rows2dict()

    trainer_client_data = sqlalchemy_result(trainer_client_data)
    trainer_client_data = trainer_client_data.rows2dict()

    if len(trainer_stats_data) == 0:
        wallet = (
            earnings
        ) = taxes = hours = sessions = categories = clients = steps = distance = None
    else:
        wallet = trainer_stats_data[0].get("wallet_balance")
        earnings = trainer_stats_data[0].get("earnings_total")
        taxes = trainer_stats_data[0].get("taxes_total")
        hours = trainer_stats_data[0].get("hours_worked")
        sessions = trainer_stats_data[0].get("sessions_worked")
        categories = trainer_stats_data[0].get("categories_assigned")
        clients = trainer_stats_data[0].get("client_count")
        steps = trainer_stats_data[0].get("steps")
        distance = trainer_stats_data[0].get("distance")

    if len(trainer_client_data) == 0:
        client_profiles = None
    else:
        client_profiles = list(
            set([pair.get("client_id") for pair in trainer_client_data])
        )

    response = dict()
    response["wallet"] = wallet
    response["earnings"] = earnings
    response["taxes"] = taxes
    response["hours"] = hours
    response["sessions"] = sessions
    response["categories"] = categories
    response["clients"] = clients
    response["client_profiles"] = client_profiles
    response["steps"] = steps
    response["distance"] = distance
    return response
