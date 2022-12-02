import datetime
import json
import os
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymysql import Timestamp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update

from api.database.database import USERDATA_ENGINE
from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens
import cv2
import time

router = APIRouter()


@router.get("/v1/profile/avatar/{user_id}", tags=["profile"])
async def get_profile_picture(user_id: str) -> json:
    "Get the profile picture of a user by their ID."
    if not os.path.exists(f"images\{user_id}\profile.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have a profile picture.",
        )

    return FileResponse(f"images\{user_id}\profile.jpeg")


@router.post("/v1/profile/avatar/{token}", tags=["profile"])
async def upload_profile_picture(token: str, file: UploadFile = File(...)) -> json:
    # if len(await file.read()) >= 20_000_000:
    #     raise HTTPException(
    #         status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    #         detail="Your file exceeds 20MB. Please reduce your file upload.",
    #     )

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
    if not os.path.exists(f"images\{user_id}\background.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have a background picture.",
        )

    return FileResponse(f"images\{user_id}\background.jpeg")


@router.post("/v1/profile/background/{token}", tags=["profile"])
async def upload_background_picture(token: str, file: UploadFile = File(...)) -> json:

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
        complete_path = path + "/background.jpeg"

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
    if not os.path.exists(f"images\{user_id}\gallery\{picture_id}.jpeg"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not have a background picture.",
        )

    return FileResponse(f"images\{user_id}\gallery\{picture_id}.jpeg")


@router.post("/v1/profile/gallery/{token}", tags=["profile"])
async def upload_gallery_picture(token: str, file: UploadFile = File(...)) -> json:

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
        path = f"./images/{uuid}/gallery"
        temp_path = path + f"/{file.filename}"
        complete_path = path + f"/{int(time.time())}.jpeg"

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
    """
    Get Profile Details
    Params:
    {
    Token: string,
    User id: number,
    }

    Returns
    {
    Name: string,
    Type: string,
    Rating: number,
    Rate: number,
    About: string,
    Goals: array:string,
    Number of photos: number,
    Partners: number,
    Trainers: number,
    Gallery: array:string
    }
    """
    pass
