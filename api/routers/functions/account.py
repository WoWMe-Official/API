import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import insert, select

from api.database.database import USERDATA_ENGINE
from api.database.functions import generate_token, hashbrown, sqlalchemy_result
from api.database.models import (
    AvailableDays,
    FitnessGoals,
    Registration,
    Specializations,
    Tokens,
    TrainerInformation,
    UserInformation,
)
from api.routers.models.account import *


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

    if signup.role.isUser:
        if (
            signup.user_information.body_fat_percentage > 100
            or signup.user_information.body_fat_percentage < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unlikely body fat percentage, please try again.",
            )

        if (
            signup.user_information.height_ft_in > 300
            or signup.user_information.height_ft_in < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unlikely height value in centimeters, please try again.",
            )

        if (
            signup.user_information.weight_lb > 1000
            or signup.user_information.weight_lb < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unlikely weight value in kilograms, please try again.",
            )

        if (
            signup.user_information.height_cm > 300
            or signup.user_information.height_cm < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unlikely height value in centimeters, please try again.",
            )

        if (
            signup.user_information.weight_kg > 1000
            or signup.user_information.weight_kg < 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unlikely weight value in kilograms, please try again.",
            )

    if signup.role.isTrainer:
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
    hashed_pass = await hashbrown(signup.personal_information.password)

    account_type_value = [1 if signup.role.isTrainer else 0]

    # personal information registration
    sql_personal_information = insert(Registration).values(
        email=signup.personal_information.email,
        password=hashed_pass,
        phone=signup.personal_information.phone,
        first_name=signup.personal_information.first_name,
        last_name=signup.personal_information.last_name,
        birthdate=signup.personal_information.birthdate,
        about_you=signup.personal_information.about_you,
        gender=signup.personal_information.gender,
        account_type=account_type_value,
        facebook=signup.personal_information.social.facebook,
        instagram=signup.personal_information.social.instagram,
    )

    sql_select_user_id = select(Registration).where(
        Registration.email == signup.personal_information.email
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
            height_ft_in=signup.user_information.height_ft_in,
            weight_lb=signup.user_information.weight_lb,
            height_cm=signup.user_information.height_cm,
            weight_kg=signup.user_information.weight_kg,
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
