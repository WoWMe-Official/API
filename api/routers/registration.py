import json

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from pymysql import Timestamp
import datetime

from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens
from sqlalchemy.sql.expression import select, update
from api.database.database import USERDATA_ENGINE
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update


router = APIRouter()


class LoginInformation(BaseModel):
    email: str
    password: str


class day(BaseModel):
    day: str
    start_time: datetime.datetime
    end_time: datetime.datetime


class socials(BaseModel):
    facebook: bool
    instagram: bool


class Signup(BaseModel):
    # generic user information
    role: str
    email: str
    password: str
    phone: str
    first_name: str
    last_name: str
    birthdate: datetime.datetime
    about_you: str
    gender: str
    available_days: List[day]
    social: socials

    # user information
    height: Optional[int]
    weight: Optional[int]
    body_fat_percentage: Optional[int]
    fitness_level: Optional[str]
    fitness_goals: Optional[List[str]]

    # trainer information
    social_security_number: Optional[int]
    identification: Optional[str]
    rate: Optional[int]
    payment_method: Optional[str]
    specializations: Optional[List[str]]
    certification_photo: Optional[str]


@router.post("/v1/login", tags=["login"])
async def login_to_your_account(login_information: LoginInformation) -> json:
    """
    Pass login information to the server in order to retrieve a login token.

    email: str, validated with direct email validation
    password: str, salted and hashed in db, db hash is compared with api has

    returns:
    token : str
    """

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
        return HTTPException(
            status_code=404, detail="User information could not be found."
        )
    return {"token": data[0].get("token")}


@router.post("/v1/sign-up", tags=["registration"])
async def sign_up_account(signup: Signup) -> json:
    return
