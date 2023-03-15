import glob
import json
import os
import time
import asyncio
import aiohttp

import cv2
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_
from sqlalchemy.sql.expression import select

from api.config import route_ip
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import (
    FitnessGoals,
    Ratings,
    Registration,
    Relationships,
    Specializations,
    Tokens,
    TrainerInformation,
    AvailableDays,
    UserInformation,
)
from api.routers.functions.general import (
    check_user_block,
    get_token_user_id,
    image_tokenizer,
)

router = APIRouter()


@router.get("/v1/profile/avatar/{user_id}", tags=["profile"])
async def get_profile_picture(user_id: str) -> json:
    "Get the profile picture of a user by their ID."
    if not os.path.exists(f"{os.getcwd()}/images/{user_id}/profile.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have a profile picture.",
        )

    image_route = f"{os.getcwd()}/images/{user_id}/profile.jpeg"
    image_token = await image_tokenizer(image_route)

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"http://{route_ip}/v1/image/{image_token}",
    )


@router.post("/v1/profile/avatar/{token}", tags=["profile"])
async def upload_profile_picture(token: str, file: UploadFile = File(...)) -> json:
    # if len(await file.read()) >= 20_000_000:
    #     raise HTTPException(
    #         status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #         detail="Your file exceeds 20MB. Please reduce your file upload.",
    #     )

    uuid = await get_token_user_id(token=token)

    try:

        contents = file.file.read()
        path = f"{os.getcwd()}/images/{uuid}"
        temp_path = path + f"/{file.filename}"
        complete_path = path + "/profile.jpeg"

        if not (os.path.exists(path=path)):
            os.mkdir(path=path)
        with open(temp_path, "wb") as f:
            f.write(contents)

        im = cv2.imread(temp_path)
        cv2.imwrite(complete_path, im, [cv2.IMWRITE_JPEG_OPTIMIZE, 9])
        os.remove(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading your profile picture. Support has been notified.",
        )
    finally:
        file.file.close()

    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your profile picture has been successfully uploaded!",
    )


@router.get("/v1/profile/background/{user_id}", tags=["profile"])
async def get_background_picture(user_id: str) -> json:
    "Get the background picture of a user by their ID."
    if not os.path.exists(f"{os.getcwd()}/images/{user_id}/header.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have a background picture.",
        )

    image_route = f"{os.getcwd()}/images/{user_id}/header.jpeg"
    image_token = await image_tokenizer(image_route)

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"http://{route_ip}/v1/image/{image_token}",
    )


@router.post("/v1/profile/background/{token}", tags=["profile"])
async def upload_background_picture(token: str, file: UploadFile = File(...)) -> json:

    uuid = await get_token_user_id(token=token)

    try:

        contents = file.file.read()
        path = f"{os.getcwd()}/images/{uuid}"
        temp_path = path + f"/{file.filename}"
        complete_path = path + "/header.jpeg"

        if not (os.path.exists(path=path)):
            os.mkdir(path=path)
        with open(temp_path, "wb") as f:
            f.write(contents)

        im = cv2.imread(temp_path)
        cv2.imwrite(complete_path, im, [cv2.IMWRITE_JPEG_OPTIMIZE, 9])
        os.remove(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading your background picture. Support has been notified.",
        )
    finally:
        file.file.close()

    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your profile background has been successfully uploaded!",
    )


@router.get("/v1/profile/gallery/{user_id}/{picture_id}", tags=["profile"])
async def get_gallery_picture(user_id: str, picture_id: str) -> json:
    "Get the gallery picture of a user by their ID and picture ID"
    if not os.path.exists(f"{os.getcwd()}/images/{user_id}/gallery/{picture_id}.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This gallery image does not exist.",
        )

    image_route = f"{os.getcwd()}/images/{user_id}/gallery/{picture_id}.jpeg"
    image_token = await image_tokenizer(image_route)

    return HTTPException(
        status_code=status.HTTP_200_OK,
        detail=f"http://{route_ip}/v1/image/{image_token}",
    )


@router.post("/v1/profile/gallery/{token}", tags=["profile"])
async def upload_gallery_picture(token: str, file: UploadFile = File(...)) -> json:

    uuid = await get_token_user_id(token=token)

    try:

        contents = file.file.read()
        root_path = f"{os.getcwd()}/images/{uuid}"
        path = f"{os.getcwd()}/images/{uuid}/gallery"
        temp_path = path + f"/{file.filename}"
        complete_path = path + f"/{int(time.time())}.jpeg"

        if not (os.path.exists(path=root_path)):
            os.mkdir(path=root_path)

        if not (os.path.exists(path=path)):
            os.mkdir(path=path)
        with open(temp_path, "wb") as f:
            f.write(contents)

        im = cv2.imread(temp_path)
        cv2.imwrite(complete_path, im, [cv2.IMWRITE_JPEG_OPTIMIZE, 9])
        os.remove(temp_path)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading your gallery picture. Support has been notified.",
        )
    finally:
        file.file.close()

    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your gallery picture has been successfully uploaded!",
    )


@router.get("/v1/profile/details/{token}/{user_id}", tags=["profile"])
async def get_profile_details(token: str, user_id: str) -> json:
    uuid = await get_token_user_id(token=token)

    if await check_user_block(blocked_id=uuid, blocker_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have been blocked by this user.",
        )

    registration_sql = select(Registration).where(Registration.user_id == user_id)
    userinformation_sql = select(UserInformation).where(
        UserInformation.user_id == user_id
    )
    fitness_goals_sql = select(FitnessGoals).where(FitnessGoals.user_id == user_id)
    ratings_sql = select(Ratings).where(Ratings.rated == user_id)
    availability_sql = select(AvailableDays).where(AvailableDays.user_id == user_id)
    relationship_sql = select(Relationships).where(
        or_(Relationships.user_id_1 == user_id, Relationships.user_id_2 == user_id)
    )
    trainer_information_sql = select(TrainerInformation).where(
        TrainerInformation.user_id == user_id
    )
    specializations_sql = select(Specializations).where(
        Specializations.user_id == user_id
    )

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            registration_data = await session.execute(registration_sql)
            userinformation_data = await session.execute(userinformation_sql)
            fitness_goals_data = await session.execute(fitness_goals_sql)
            availability_data = await session.execute(availability_sql)
            ratings_data = await session.execute(ratings_sql)
            relationship_data = await session.execute(relationship_sql)

    registration_data = sqlalchemy_result(registration_data)
    registration_data = registration_data.rows2dict()
    if len(registration_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="This user does not exist."
        )
    else:
        name = (
            registration_data[0].get("first_name")
            + " "
            + registration_data[0].get("last_name")
        )
        about = registration_data[0].get("about_you")
        gender = registration_data[0].get("gender")
        socials = dict()
        socials["facebook"] = registration_data[0].get("facebook")
        socials["instagram"] = registration_data[0].get("instagram")

    if registration_data[0].get("account_type") == 1:
        async with USERDATA_ENGINE.get_session() as session:
            session: AsyncSession = session
            async with session.begin():
                trainer_information_data = await session.execute(
                    trainer_information_sql
                )
                specialization_data = await session.execute(specializations_sql)

        trainer_information_data = sqlalchemy_result(trainer_information_data)
        trainer_information_data = trainer_information_data.rows2dict()
        rate = trainer_information_data[0].get("rate")
        payment_method = trainer_information_data[0].get("payment_method")

        specialization_data = sqlalchemy_result(specialization_data)
        specialization_data = specialization_data.rows2dict()

        specializations = []
        for specialization in specialization_data:
            specializations.append(specialization.get("specialization"))

    else:
        rate = None
        payment_method = None
        specializations = None

    availability_data = sqlalchemy_result(availability_data)
    availability_data = availability_data.rows2dict()
    if len(availability_data) == 0:
        availability = None
    else:
        availability = []
        for available_day in availability_data:
            d = dict()
            d["day"] = available_day.get("day")
            d["start_time"] = available_day.get("start_time")
            d["end_time"] = available_day.get("end_time")
            availability.append(d)

    userinformation_data = sqlalchemy_result(userinformation_data)
    userinformation_data = userinformation_data.rows2dict()
    if len(userinformation_data) != 0:

        fitness_level = userinformation_data[0].get("fitness_level")
        body_fat_percentage = userinformation_data[0].get("body_fat_percentage")
        weight_kg = userinformation_data[0].get("weight_kg")
        height_cm = userinformation_data[0].get("height_cm")
        weight_lb = userinformation_data[0].get("weight_lb")
        height_ft_in = userinformation_data[0].get("height_ft_in")
    else:
        fitness_level = None
        body_fat_percentage = None
        weight_kg = None
        height_cm = None
        weight_lb = None
        height_ft_in = None

    fitness_goals_data = sqlalchemy_result(fitness_goals_data)
    fitness_goals_data = fitness_goals_data.rows2dict()
    if len(fitness_goals_data) == 0:
        goals = None
    else:
        goals = []
        for g in fitness_goals_data:
            goals.append(g.get("goal"))

    ratings_data = sqlalchemy_result(ratings_data)
    ratings_data = ratings_data.rows2dict()
    if len(ratings_data) == 0:
        ratings = None
    else:
        ratings = sum([rating.get("rating") for rating in ratings]) / (len(ratings)) * 5

    account_type_value = registration_data[0].get("account_type")
    if account_type_value == 0:
        account_type = "User"
    elif account_type_value == 1:
        account_type = "Trainer"
    else:
        account_type = "Other"

    relationship_data = sqlalchemy_result(relationship_data)
    relationship_data = relationship_data.rows2dict()
    if len(relationship_data) == 0:
        partners = 0
        trainers = 0
    else:
        relationships = [int(r.get("relationship_type")) for r in relationship_data]
        partners = relationships.count(0)
        trainers = relationships.count(1)

    path = f"{os.getcwd()}/images/{user_id}/gallery/*"
    files = glob.glob(path)
    photo_count = len(files)
    gallery = [os.path.basename(x)[:-5] for x in files]

    ## dict construction

    response = dict()

    ## public dict

    public = dict()
    public["name"] = name
    public["about"] = about
    public["gender"] = gender
    public["socials"] = socials
    public["availability"] = availability
    public["type"] = account_type
    public["goals"] = goals
    public["rate"] = rate
    public["payment_method"] = payment_method
    public["partners"] = partners
    public["trainers"] = trainers
    public["rating"] = ratings
    public["photo_count"] = photo_count
    public["gallery"] = gallery
    public["specializations"] = specializations
    public["fitness_level"] = fitness_level
    public["body_fat_percentage"] = body_fat_percentage
    public["weight_kg"] = weight_kg
    public["height_cm"] = height_cm
    public["weight_lb"] = weight_lb
    public["height_ft_in"] = height_ft_in

    response["public"] = public
    ## if querying self profile

    if int(uuid) == int(user_id):
        private = dict()
        private["birthdate"] = registration_data[0].get("birthdate")
        private["phone"] = registration_data[0].get("phone")

        response["private"] = private

    return response


@router.get("/v1/profile/search/", tags=["profile"])
async def search_profile(
    token: str,
    account_type: int = None,
    first_name: str = None,
    last_name: str = None,
    gender: str = None,
) -> json:
    uuid = await get_token_user_id(token=token)

    sql = select(Registration)

    if (account_type == 1) or (account_type == 0):
        sql = sql.where(Registration.account_type == account_type)

    if first_name:
        sql = sql.where(Registration.first_name == first_name)

    if last_name:
        sql = sql.where(Registration.last_name == last_name)

    if gender:
        sql = sql.where(Registration.gender == gender)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    user_ids = []
    for user in result:
        user_id = user.get("user_id")
        if user_id != None:
            user_ids.append(user_id)

    user_ids = list(set(user_ids))

    return HTTPException(status_code=status.HTTP_200_OK, detail=user_ids)


@router.get("/v1/profile/full-search/", tags=["profile"])
async def search_full_profile(
    token: str,
    account_type: int = None,
    first_name: str = None,
    last_name: str = None,
    gender: str = None,
) -> json:

    await get_token_user_id(token=token)

    sql = select(Registration)

    if (account_type == 1) or (account_type == 0):
        sql = sql.where(Registration.account_type == account_type)

    if first_name:
        sql = sql.where(Registration.first_name == first_name)

    if last_name:
        sql = sql.where(Registration.last_name == last_name)

    if gender:
        sql = sql.where(Registration.gender == gender)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            result = await session.execute(sql)

    result = sqlalchemy_result(result)
    result = result.rows2dict()

    user_ids = []
    for user in result:
        user_id = user.get("user_id")
        if user_id != None:
            user_ids.append(user_id)

    user_ids = list(set(user_ids))

    ## user ids

    responses = []
    for u_id in user_ids:
        response = await get_profile_details(token=token, user_id=u_id)
        responses.append(response)

    return responses
