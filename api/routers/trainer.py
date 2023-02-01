import json
import os
import cv2
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update

from api.config import route_ip
from api.database.database import USERDATA_ENGINE
from api.database.functions import sqlalchemy_result
from api.database.models import (
    Tokens,
    TrainerInformation,
    Registration,
    Specializations,
)
from api.routers.functions.general import image_tokenizer, get_token_user_id

router = APIRouter()


@router.get("/v1/trainers/id-search/{token}", tags=["trainer"])
async def search_id_trainers(
    token: str,
    min_payment: int = None,
    max_payment: int = None,
    first_name: str = None,
    last_name: str = None,
    specialization: str = None,
    max_results: int = None,
) -> json:
    """search for trainers, returns user ID of trainer"""

    await get_token_user_id(token=token)
    sql = select(TrainerInformation)
    sql = sql.join(Registration, TrainerInformation.user_id == Registration.user_id)
    sql = sql.join(
        Specializations, TrainerInformation.user_id == Specializations.user_id
    )

    if min_payment:
        sql = sql.where(TrainerInformation.rate >= min_payment)

    if max_payment:
        sql = sql.where(TrainerInformation.rate <= max_payment)

    if first_name:
        sql = sql.where(Registration.first_name == first_name)

    if last_name:
        sql = sql.where(Registration.last_name == last_name)

    if specialization:
        sql = sql.where(Specializations.specialization == specialization)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)
    data = sqlalchemy_result(data)
    data = data.rows2dict()

    trainer_ids = []
    for d in data:
        trainer_ids.append(d["user_id"])

    response = list(set(trainer_ids))

    return HTTPException(status_code=status.HTTP_200_OK, detail=response)


@router.post("/v1/trainer/identification/upload/{token}", tags=["trainer"])
async def upload_identification(token: str, file: UploadFile = File(...)) -> json:

    sql = select(Tokens).where(Tokens.token == token)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()
    uuid = data[0].get("user_id")

    try:
        contents = file.file.read()
        path = f"{os.getcwd()}/images/{uuid}"
        temp_path = path + f"/{file.filename}"
        complete_path = path + "/identification.jpeg"

        if not (os.path.exists(path=path)):
            os.mkdir(path=path)
        with open(temp_path, "wb") as f:
            f.write(contents)

        im = cv2.imread(temp_path)
        cv2.imwrite(complete_path, im, [cv2.IMWRITE_JPEG_OPTIMIZE, 9])
        os.remove(temp_path)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading your identification. Support has been notified.",
        )
    finally:
        file.file.close()

    complete_path = path + "/identification.png"
    sql = (
        update(TrainerInformation)
        .where(TrainerInformation.user_id == uuid)
        .values(identification=complete_path)
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your identification has been successfully uploaded!",
    )


@router.get("/v1/trainer/identification/evaluate", tags=["trainer"])
async def evaluate_identification(token: str, user_id: int) -> json:
    sql = select(Tokens).where(Tokens.token == token)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()
    auth_level = data[0].get("auth_level")

    if not os.path.exists(f"{os.getcwd()}/images/{user_id}/identification.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user has not uploaded any identification.",
        )

    if auth_level == 9:
        image_route = f"{os.getcwd()}/images/{user_id}/identification.jpeg"
        image_token = await image_tokenizer(image_route)

        return HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"http://{route_ip}/v1/image/{image_token}",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have the necessary permissions to evaluate this account.",
        )


@router.post("/v1/trainer/certification/upload/{token}", tags=["trainer"])
async def upload_certification(token: str, file: UploadFile = File(...)) -> json:

    sql = select(Tokens).where(Tokens.token == token)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()
    uuid = data[0].get("user_id")

    try:
        contents = file.file.read()
        path = f"{os.getcwd()}/images/{uuid}"
        temp_path = path + f"/{file.filename}"
        complete_path = path + "/certification.jpeg"

        if not (os.path.exists(path=path)):
            os.mkdir(path=path)
        with open(temp_path, "wb") as f:
            f.write(contents)

        im = cv2.imread(temp_path)
        cv2.imwrite(complete_path, im, [cv2.IMWRITE_JPEG_OPTIMIZE, 9])
        os.remove(temp_path)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading your certification. Support has been notified.",
        )
    finally:
        file.file.close()

    complete_path = path + "/certification.png"
    sql = (
        update(TrainerInformation)
        .where(TrainerInformation.user_id == uuid)
        .values(certification_photo=complete_path)
    )
    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    raise HTTPException(
        status_code=status.HTTP_201_CREATED,
        detail="Your certification has been successfully uploaded!",
    )


@router.get("/v1/trainer/certification/evaluate", tags=["trainer"])
async def evaluate_certification(token: str, user_id: int) -> json:
    sql = select(Tokens).where(Tokens.token == token)

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    data = data.rows2dict()
    auth_level = data[0].get("auth_level")

    if not os.path.exists(f"{os.getcwd()}/images/{user_id}/certification.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user has not uploaded any certification.",
        )

    if auth_level == 9:
        image_route = f"{os.getcwd()}/images/{user_id}/certification.jpeg"
        image_token = await image_tokenizer(image_route)

        return HTTPException(
            status_code=status.HTTP_200_OK,
            detail=f"http://{route_ip}/v1/image/{image_token}",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have the necessary permissions to evaluate this account.",
        )
