import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, insert, delete, update

import api.routers.functions.account as account_functions
import api.routers.models.account as account_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import (
    Registration,
    Tokens,
    Blocks,
    TrainerInformation,
    UserInformation,
    Specializations,
    FitnessGoals,
    AvailableDays,
)
from api.routers.functions.general import get_token_user_id

router = APIRouter()


@router.post("/sign-up", tags=["account"])
async def sign_up(signup: account_models.signup) -> json:
    """
    This code defines a function sign_up that registers an account with WoWMe. The function performs several checks on the provided account details and raises HTTPException with corresponding status codes and details if any check fails. If all checks pass, the function calls the sign_up_account function from account_functions to create the account.
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


@router.put("/change-password", tags=["account"])
async def change_password(email: str, old_password: str, new_password: str) -> json:
    """
    This is a PUT API endpoint for changing the password of a registered user. It takes in the user's email, old password, and new password. The email is first sanitized and both old and new passwords are hashed. The API endpoint then checks if the old password matches the email address provided, and if so, updates the password with the new hash. If the old password does not match, an HTTPException is raised with a 401 error status code. If the update is successful, an HTTPException is raised with a 202 status code indicating that the password has been changed."""
    email = await account_functions.sanitize_email(email=email)
    old_hashed_password = await hashbrown(password=old_password)
    new_hashed_password = await hashbrown(password=new_password)

    sql = select(Registration).where(
        Registration.email == email, Registration.password == old_hashed_password
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    results = sqlalchemy_result(data)
    results = results.rows2dict()
    if len(results) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect, please try again.",
        )

    uuid = results[0].get("user_id")

    sql = (
        update(Registration)
        .where(Registration.user_id == uuid)
        .values(password=new_hashed_password)
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail="Password changed.",
    )


@router.put("/edit/{token}", tags=["account"])
async def edit_account_details(
    token: str, signup: account_models.edit_account_details
) -> json:
    """This code defines an asynchronous HTTP PUT request to edit user account details. It takes a token and a signup object as parameters, where signup is a Pydantic model. The function first retrieves the user ID associated with the token, and then updates the database based on the fields in signup. Depending on the fields specified, the function updates the Registration, TrainerInformation, UserInformation, AvailableDays, Specializations, or Account database tables. The function executes the database updates in separate sessions to maintain database integrity. The function returns a JSON response."""
    uuid = await get_token_user_id(token=token)

    if signup.edit_personal_details:
        sql_registration = update(Registration).where(Registration.user_id == uuid)
        personal_details_dict = dict()

        if signup.edit_personal_details.first_name:
            personal_details_dict[
                "first_name"
            ] = signup.edit_personal_details.first_name

        if signup.edit_personal_details.last_name:
            personal_details_dict["last_name"] = signup.edit_personal_details.last_name

        if signup.edit_personal_details.phone:
            personal_details_dict["phone"] = signup.edit_personal_details.phone

        if signup.edit_personal_details.birthdate:
            personal_details_dict["birthdate"] = signup.edit_personal_details.birthdate

        if signup.edit_personal_details.about_you:
            personal_details_dict["about_you"] = signup.edit_personal_details.about_you

        if signup.edit_personal_details.gender:
            personal_details_dict["gender"] = signup.edit_personal_details.gender

        if signup.edit_personal_details.social:
            personal_details_dict[
                "facebook"
            ] = signup.edit_personal_details.social.facebook
            personal_details_dict[
                "instagram"
            ] = signup.edit_personal_details.social.instagram

        sql_registration = sql_registration.values(personal_details_dict)

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                await session.execute(sql_registration)

    if signup.edit_role:
        sql_account_type = update(Registration).where(Registration.user_id == uuid)
        account_type_value = [1 if signup.edit_role.isTrainer else 0][0]
        sql_account_type = sql_account_type.values(account_type=account_type_value)

        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                await session.execute(sql_account_type)

    if signup.edit_trainer_information:

        trainer_information_sql = update(TrainerInformation).where(
            TrainerInformation.user_id == uuid
        )

        trainer_information_dict = dict()
        if signup.edit_trainer_information.payment_method:
            trainer_information_dict[
                "payment_method"
            ] = signup.edit_trainer_information.payment_method

        if signup.edit_trainer_information.rate:
            trainer_information_dict["rate"] = signup.edit_trainer_information.rate

        if signup.edit_trainer_information.social_security_number:
            trainer_information_dict[
                "social_security_number"
            ] = signup.edit_trainer_information.social_security_number
        trainer_information_sql = trainer_information_sql.values(
            trainer_information_dict
        )

        if trainer_information_dict:
            async with USERDATA_ENGINE.get_session() as session:
                session: AsyncSession = session
                async with session.begin():
                    await session.execute(trainer_information_sql)

        if signup.edit_trainer_information.specializations:
            specialization_list = []
            for specialization in signup.edit_trainer_information.specializations:
                pack = dict()
                pack["user_id"] = uuid
                pack["specialization"] = specialization
                specialization_list.append(pack)

            sql_delete_specializations = delete(Specializations).where(
                Specializations.user_id == uuid
            )
            sql_insert_specializations = insert(Specializations).values(
                specialization_list
            )

            async with USERDATA_ENGINE.get_session() as session:
                session: AsyncSession = session
                async with session.begin():
                    await session.execute(sql_delete_specializations)
                    await session.execute(sql_insert_specializations)

    if signup.edit_user_information:
        sql_user_information = update(UserInformation).where(
            UserInformation.user_id == uuid
        )

        user_information_dict = dict()
        if signup.edit_user_information.height_ft_in:
            user_information_dict[
                "height_ft_in"
            ] = signup.edit_user_information.height_ft_in
        if signup.edit_user_information.weight_lb:
            user_information_dict["weight_lb"] = signup.edit_user_information.weight_lb
        if signup.edit_user_information.height_cm:
            user_information_dict["height_cm"] = signup.edit_user_information.height_cm
        if signup.edit_user_information.weight_kg:
            user_information_dict["weight_kg"] = signup.edit_user_information.weight_kg
        if signup.edit_user_information.body_fat_percentage:
            user_information_dict[
                "body_fat_percentage"
            ] = signup.edit_user_information.body_fat_percentage
        if signup.edit_user_information.fitness_level:
            user_information_dict[
                "fitness_level"
            ] = signup.edit_user_information.fitness_level

        sql_user_information = sql_user_information.values(user_information_dict)

        if user_information_dict:
            async with USERDATA_ENGINE.get_session() as session:
                session: AsyncSession = session
                async with session.begin():
                    await session.execute(sql_user_information)

        if signup.edit_user_information.available_days:

            availability = []
            for day in signup.edit_user_information.available_days:
                pack = dict()
                pack["user_id"] = uuid
                pack["day"] = day.day
                pack["start_time"] = day.start_time
                pack["end_time"] = day.end_time
                availability.append(pack)

            sql_insert_available_days = insert(AvailableDays).values(availability)
            sql_delete_available_days = delete(AvailableDays).where(
                AvailableDays.user_id == uuid
            )

            async with USERDATA_ENGINE.get_session() as session:
                session: AsyncSession = session
                async with session.begin():
                    await session.execute(sql_delete_available_days)
                    await session.execute(sql_insert_available_days)

        if signup.edit_user_information.fitness_goals:
            goals = []
            for fitness_goal in signup.edit_user_information.fitness_goals:
                pair = dict()
                pair["user_id"] = uuid
                pair["goal"] = fitness_goal
                goals.append(pair)

            sql_delete_goals = delete(FitnessGoals).where(FitnessGoals.user_id == uuid)
            sql_insert_goals = insert(FitnessGoals).values(goals)

            async with USERDATA_ENGINE.get_session() as session:
                session: AsyncSession = session
                async with session.begin():
                    await session.execute(sql_delete_goals)
                    await session.execute(sql_insert_goals)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="Updated account information."
    )


@router.post("/login", tags=["account"])
async def login_to_your_account(
    login_information: account_models.login_information,
) -> json:
    """This code defines an HTTP POST endpoint "/login" with a single input parameter 'login_information' of a custom class 'account_models.login_information'. The endpoint is tagged under "account".

    The function uses the input email and password to query a database table (Tokens) with a JOIN condition to another table (Registration) using SQLAlchemy. If the query returns no data, an HTTPException is raised with a status code of 401 and the detail message "Access not permitted". If the query returns data, the function creates a response dictionary with keys "token" and "user_id" and their corresponding values taken from the query result. Finally, the function returns the response dictionary as JSON."""
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


@router.post("/block/{token}/{user_id}", tags=["account"])
async def block_user(token: str, user_id: str) -> json:
    """
    This code defines an API endpoint that allows users to block another user by sending a POST request with a valid authentication token and the user ID of the user to be blocked in the URL. The function retrieves the UUID of the authenticated user using the authentication token, then inserts a new record in the "Blocks" table in the database with the UUID of the authenticated user and the user ID of the user to be blocked. If the insertion is successful, the function returns a HTTP 201 status code with a message indicating that the user has been blocked.
    """
    uuid = await get_token_user_id(token=token)

    insert_block = insert(Blocks).values(blocked_id=user_id, blocker_id=uuid)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(insert_block)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED, detail="User has been blocked."
    )


@router.post("/unblock/{token}/{user_id}", tags=["account"])
async def unblock_user(token: str, user_id: str) -> json:
    """
    This is a Python FastAPI endpoint for unblocking a user. The endpoint is decorated with @router.post() and accepts two path parameters, token and user_id. It calls the get_token_user_id() function to get the user ID for the token. It then creates a SQLAlchemy delete() statement to remove a row from the Blocks table where the blocked_id column matches user_id and the blocker_id column matches the user ID for the token. The delete() statement is executed in an async session and an HTTPException with a status code of 202 and a detail message of "User has been unblocked." is raised.
    """
    uuid = await get_token_user_id(token=token)

    remove_block = delete(Blocks).where(
        Blocks.blocked_id == user_id, Blocks.blocker_id == uuid
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            await session.execute(remove_block)

    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED, detail="User has been unblocked."
    )
