import json

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from pymysql import Timestamp
import datetime
import os

from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens
from sqlalchemy.sql.expression import select, update
from api.database.database import USERDATA_ENGINE
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, update
from fastapi import File, UploadFile

router = APIRouter()


@router.get("/v1/profile/thumbnail/{user_id}", tags=["profile"])
async def get_profile_information(user_id: str, token: str) -> json:
    """returns profile picture string, and user id"""


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


@router.get("/v1/profile-details/{token}/{user_id}", tags=["profile"])
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
