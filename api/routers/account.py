import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

import api.routers.functions.account as account_functions
import api.routers.models.account as account_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens

router = APIRouter()


@router.post("/v1/account/sign-up", tags=["account"])
async def sign_up(signup: account_models.signup) -> json:
    """
    Register an account with Workout With Me.
    """
    await account_functions.sanity_check(signup=signup)

    if signup.role.isTrainer == signup.role.isUser == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please mark your account as a trainer, user, or both.",
        )

    if (signup.role.isTrainer == True) & (signup.trainer_information == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing trainer sign-up information. Please try again with the correct information attached in payload.",
        )

    if (signup.role.isUser == True) & (signup.user_information == None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user sign-up information. Please try again with the correct information attached in payload.",
        )

    signup.personal_information.email = await account_functions.sanitize_email(
        signup.personal_information.email
    )

    if not signup.personal_information.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is incorrect format, please try again.",
        )

    if await account_functions.examine_email(email=signup.personal_information.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email presently exists. Try logging in with your email, or reset your password below.",
        )
    await account_functions.sign_up_account(signup=signup)


@router.post("/v1/account/login", tags=["account"])
async def login_to_your_account(
    login_information: account_models.login_information,
) -> json:
    email = login_information.email
    password = await hashbrown(login_information.password)

    sql = select(Tokens)
    sql = sql.join(Registration, Tokens.user_id == Registration.user_id)
    sql = sql.where(Registration.email == email)
    sql = sql.where(Registration.password == password)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    if len(data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not permitted."
        )
    response = dict()
    response["token"] = data[0].get("token")
    response["user_id"] = data[0].get("user_id")
    return response
