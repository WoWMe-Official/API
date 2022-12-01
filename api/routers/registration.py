import json

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from pymysql import Timestamp
import datetime
import re

from api.database.functions import hashbrown, sqlalchemy_result, generate_token
from api.database.models import (
    Registration,
    Tokens,
    UserInformation,
    Genders,
    AvailableDays,
    FitnessGoals,
    FitnessLevel,
    TrainerInformation,
    Specializations,
)
from sqlalchemy.sql.expression import select, update, insert
from api.database.database import USERDATA_ENGINE
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


class login_details(BaseModel):
    email: str
    password: str


class day(BaseModel):
    day: int
    start_time: datetime.datetime
    end_time: datetime.datetime


class socials(BaseModel):
    facebook: bool
    instagram: bool


class role(BaseModel):
    isTrainer: bool
    isUser: bool


class user_information(BaseModel):
    available_days: List[day]
    height: Optional[int]
    weight: Optional[int]
    body_fat_percentage: Optional[int]
    fitness_level: Optional[int]
    fitness_goals: Optional[List[str]]


class trainer_information(BaseModel):
    social_security_number: Optional[int]
    rate: Optional[int]
    payment_method: Optional[str]
    specializations: Optional[List[str]]


class personal_information(BaseModel):
    email: str
    password: str
    phone: str
    first_name: str
    last_name: str
    birthdate: datetime.datetime
    about_you: str
    gender: int
    social: Optional[socials]


class signup(BaseModel):
    personal_information: personal_information
    role: role
    user_information: Optional[user_information]
    trainer_information: Optional[trainer_information]


class login_information(BaseModel):
    email: str
    password: str


@router.post("/v1/sign-up", tags=["registration"])
async def sign_up_account(signup: signup) -> json:
    """
    Pass signup details to account registration pathway
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


async def sanitize_email(email: str):
    if len(email) > 254:
        return None
    email = email.strip(" ")
    if email.count("@") != 1:
        return None
    return email


async def sanity_check(signup: signup):
    if not re.fullmatch(
        pattern="^[A-Za-z0-9-_ ]*$", string=signup.personal_information.first_name
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported name format, please try again.",
        )

    if not re.fullmatch(
        pattern="^[A-Za-z0-9-_ ]*$", string=signup.personal_information.last_name
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported name format, please try again.",
        )

    if not re.fullmatch(
        pattern="^[\(\)0-9-]*$", string=signup.personal_information.phone
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported phone format, please try again.",
        )

    if not re.fullmatch(
        pattern="^[A-Za-z0-9!@#$%^&*\(\)-_ ]{1,128}$",
        string=signup.personal_information.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported password format, please try again.",
        )

    if (
        signup.user_information.body_fat_percentage > 100
        or signup.user_information.body_fat_percentage < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unlikely body fat percentage, please try again.",
        )

    if signup.user_information.height > 300 or signup.user_information.height < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unlikely height value in centimeters, please try again.",
        )

    if signup.user_information.weight > 1000 or signup.user_information.weight < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unlikely weight value in kilograms, please try again.",
        )

    if not re.fullmatch(
        pattern="^\d{3}-\d{2}-\d{4}$",
        string=signup.trainer_information.social_security_number,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported social security number format, please try again.",
        )

    if signup.trainer_information.rate < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unlikely trainer rate, please try again.",
        )


async def examine_email(email: str):
    registration = Registration
    sql = select(registration).where(registration.email == email)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()

    if len(data) == 0:
        return False
    return True


async def sign_up_account(signup: signup):
    registration = Registration

    hashed_pass = await hashbrown(signup.personal_information.password)

    # personal information registration
    sql_personal_information = insert(registration).values(
        email=signup.personal_information.email,
        password=hashed_pass,
        phone=signup.personal_information.phone,
        first_name=signup.personal_information.first_name,
        last_name=signup.personal_information.last_name,
        birthdate=signup.personal_information.birthdate,
        about_you=signup.personal_information.about_you,
        gender=signup.personal_information.gender,
        facebook=signup.personal_information.social.facebook,
        instagram=signup.personal_information.social.instagram,
    )

    sql_select_user_id = select(registration).where(
        registration.email == signup.personal_information.email
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_personal_information)
            uuid_selection = await session.execute(sql_select_user_id)

    uuid_result = sqlalchemy_result(uuid_selection)
    uuid_result = uuid_result.rows2dict()
    uuid = uuid_result[0].get("user_id")
    if not uuid:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A server-side error occured during registration. Support is on the way!",
        )

    if signup.role.isUser:
        sql_insert_user_information = insert(UserInformation).values(
            user_id=uuid,
            height=signup.user_information.height,
            weight=signup.user_information.weight,
            body_fat_percentage=signup.user_information.body_fat_percentage,
            fitness_level=signup.user_information.fitness_level,
        )
        goals = []

        for fitness_goal in signup.user_information.fitness_goals:
            pair = dict()
            pair["user_id"] = uuid
            pair["goal"] = fitness_goal
            goals.append(pair)

        sql_insert_goals = insert(FitnessGoals).values(goals)

        availability = []
        for day in signup.user_information.available_days:
            pack = dict()
            pack["user_id"] = uuid
            pack["day"] = day.day
            pack["start_time"] = day.start_time
            pack["end_time"] = day.end_time
            availability.append(pack)

        sql_insert_available_days = insert(AvailableDays).values(availability)

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                await session.execute(sql_insert_user_information)
                await session.execute(sql_insert_goals)
                await session.execute(sql_insert_available_days)

    if signup.role.isTrainer:

        sql_insert_trainer_information = insert(TrainerInformation).values(
            user_id=uuid,
            social_security_number=signup.trainer_information.social_security_number,
            rate=signup.trainer_information.rate,
            payment_method=signup.trainer_information.payment_method,
        )

        specialization_list = []
        for specialization in signup.trainer_information.specializations:
            pack = dict()
            pack["user_id"] = uuid
            pack["specialization"] = specialization
            specialization_list.append(pack)
        sql_insert_specializations = insert(Specializations).values(specialization_list)

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                await session.execute(sql_insert_trainer_information)
                await session.execute(sql_insert_specializations)

    authorization_token = await generate_token()
    sql_create_token = insert(Tokens).values(
        token=authorization_token, user_id=uuid, auth_level=0
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(sql_create_token)
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail=authorization_token)


@router.post("/v1/login", tags=["login"])
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
