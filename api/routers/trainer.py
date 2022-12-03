import json

from fastapi import APIRouter

from api.database.functions import sqlalchemy_result
from api.database.models import Tokens, TrainerInformation
from sqlalchemy.sql.expression import select, update
from api.database.database import USERDATA_ENGINE
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update
from fastapi.responses import FileResponse
import cv2
import os

router = APIRouter()


@router.get("/v1/trainers/{token}", tags=["trainer"])
async def get_trainer_information(token: str) -> json:
    """
    Background image: string,
    Title: string,
    Number of  exercises: number,
    Difficulty: string
    """


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
        path = f"./images/{uuid}"
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

    if not os.path.exists(f"images\{user_id}\identification.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user has not uploaded any identification.",
        )

    if auth_level == 9:
        return FileResponse(f"images\{user_id}\identification.jpeg")
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
        path = f"./images/{uuid}"
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

    if not os.path.exists(f"images\{user_id}\certification.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user has not uploaded any certification.",
        )

    if auth_level == 9:
        return FileResponse(f"images\{user_id}\certification.jpeg")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have the necessary permissions to evaluate this account.",
        )
