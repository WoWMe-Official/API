import json
import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from api.database.database import USERDATA_ENGINE
from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens
from api.routers.functions.account import *
from api.routers.models.account import *

router = APIRouter()


@router.post("/v1/account/sign-up", tags=["account"])
async def sign_up_account(signup: signup) -> json:
    """
    Register an account with Workout With Me.
    """
    await sanity_check(signup=signup)

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

    signup.personal_information.email = await sanitize_email(
        signup.personal_information.email
    )
    if not signup.personal_information.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is incorrect format, please try again.",
        )

    if await examine_email(email=signup.personal_information.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email presently exists. Try logging in with your email, or reset your password below.",
        )

    await sign_up_account(signup=signup)


@router.post("/v1/account/login", tags=["account"])
async def login_to_your_account(login_information: login_information) -> json:
    email = login_information.email
    password = await hashbrown(login_information.password)

    registrationTable = Registration
    tokensTable = Tokens
    sql = select(tokensTable)
    sql = sql.where(registrationTable.email == email)
    sql = sql.where(registrationTable.password == password)

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
    raise HTTPException(status_code=status.HTTP_200_OK, detail=data[0].get("token"))


@router.post("/v1/profile/thumbnail/{token}", tags=["profile"])
async def post_profile_picture(token: str, file: UploadFile = File(...)) -> json:
    # get user id from token

    user_id = "test"

    try:
        contents = file.file.read()
        os.mkdir(f"./images/{user_id}")
        with open(f"./images/{user_id}/{file.filename}", "wb") as f:
            f.write(contents)
    except Exception:
        return {"message": "File could not be uploaded. Try again later!"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
