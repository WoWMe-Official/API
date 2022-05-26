import json
import os
import shutil
from datetime import datetime
from enum import Enum
from pickletools import optimize
from typing import Optional
from urllib.request import Request

from api.database.functions import (
    USERDATA_ENGINE,
    EngineType,
    image_token_generator,
    sqlalchemy_result,
    verify_token,
)
from api.database.models import UserImages
from api.routers.users import get_users
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from genericpath import exists
from pydantic import BaseModel
from pydantic.fields import Field
from pymysql import Timestamp
from pyparsing import Opt
from sqlalchemy import BLOB, DATETIME, TIMESTAMP, func, select
from sqlalchemy.dialects.mysql import Insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select, insert, select

router = APIRouter()


class image_category(str, Enum):
    bio = "bio"
    profile = "profile"
    banner = "banner"
    chat = "chat"
    license_front = "license_front"
    license_back = "license_back"


@router.get(
    "/V1/user-images/",
    tags=["user", "images"],
)
async def get_user_images(
    token: str,
    login: str,
    s_user_id: Optional[int] = None,
    chat: Optional[bool] = False,
    profile: Optional[bool] = False,
    bio: Optional[bool] = False,
    banner: Optional[bool] = False,
    image_key: Optional[str] = None,
    size: Optional[int] = None,
    timestamp: Optional[datetime] = None,
    ID: Optional[int] = None,
    image: UploadFile = File(None),
    row_count: Optional[int] = Query(100, ge=1, le=1000),
    page: Optional[int] = Query(1, ge=1),
) -> json:
    """
    Args:\n
        token (str): user token information\n
        login (str): user login information\n
        s_user_id (Optional[int], optional): sending user id. Defaults to None.\n
        chat (Optional[bool], optional): True if the content is chat. Defaults to False.\n
        profile (Optional[bool], optional): True if the content is a profile. Defaults to False.\n
        bio (Optional[bool], optional): True if the content is in a bio. Defaults to False.\n
        banner (Optional[bool], optional): True if the content is a banner image. Defaults to False.\n
        image_key (Optional[str], optional): The image key for the image. Defaults to None.\n
        size (Optional[int], optional): The size of the image in KB. Defaults to None.\n
        timestamp (Optional[datetime], optional): timestamp of image creation. Defaults to None.\n
        ID (Optional[int], optional): ID of the image, increments automatically. Defaults to None.\n
        image (UploadFile, optional): Image path on server itself. Defaults to File(None).\n
        row_count (Optional[int], optional): Rows to pull for relevant data. Defaults to Query(100, ge=1, le=1000).\n
        page (Optional[int], optional): Pages to pull. Defaults to Query(1, ge=1).\n
    Returns:\n
        json: _description_\n
    """

    if not await verify_token(login=login, token=token, access_level=9):
        return

    table = UserImages
    sql: Select = select(table)

    if s_user_id is not None:
        sql = sql.where(table.s_user_id == s_user_id)

    if chat is not None:
        sql = sql.where(table.chat == chat)

    if profile is not None:
        sql = sql.where(table.profile == profile)

    if bio is not None:
        sql = sql.where(table.bio == bio)

    if banner is not None:
        sql = sql.where(table.banner == banner)

    if image_key is not None:
        sql = sql.where(table.image_key == image_key)

    if size is not None:
        sql = sql.where(table.size == size)

    if timestamp is not None:
        sql = sql.where(table.timestamp == timestamp)

    if ID is not None:
        sql = sql.where(table.ID == ID)

    if image is not None:
        sql = sql.where(table.image == image)

    sql = sql.limit(row_count).offset(row_count * (page - 1))

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post(
    "/V1/user-images",
    tags=["user", "images"],
)
async def post_user_images(
    login: str,
    token: str,
    selection: image_category,
    image: UploadFile = File(...),
) -> json:
    """
    Args:\n
        login (str): Login informatoin\n
        token (str): Token informatoin\n
        selection (image_category): Image category selection for categorization.\n
        image (UploadFile, optional): Uploaded image. Defaults to File(...).\n

    Returns:\n
        json: {'ok':'ok'}\n
    """

    # verify user auth level
    if not await verify_token(login=login, token=token, access_level=9):
        return

    # get user ID
    user_data = await get_users(login=login, token=token, self_lookup=True)
    user_id = user_data[0]["user_id"]

    # generate image key
    image_key = await image_token_generator(length=50)

    # set directory
    directory = f"images/{user_id}"
    image_path = f"{directory}/{image_key}"

    # create directory
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

    # store image in directory
    with open(image_path, "wb") as image_buffer:
        shutil.copyfileobj(image.file, image_buffer)

    # image size in KB
    size = os.path.getsize(image_path) / 1000

    # set up selection name and relevant values for
    selection_choice = selection.name
    bio = profile = banner = chat = license_front = license_back = 0

    if selection_choice == "bio":
        bio = 1
    if selection_choice == "profile":
        profile = 1
    if selection_choice == "banner":
        banner = 1
    if selection_choice == "chat":
        chat = 1
    if selection_choice == "license_front":
        license_front = 1
    if selection_choice == "license_back":
        license_back = 1

    values = {
        "s_user_id": user_id,
        "chat": chat,
        "profile": profile,
        "bio": bio,
        "banner": banner,
        "image_key": image_key,
        "image": image_path,
        "size": size,
    }

    table = UserImages
    sql = insert(table).values(values)
    sql = sql.prefix_with("ignore")

    async with USERDATA_ENGINE.get_session() as session:
        session: AsyncSession = session
        async with session.begin():
            data = await session.execute(sql)

    return {"ok": "ok"}
