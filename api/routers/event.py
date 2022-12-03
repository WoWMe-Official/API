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


@router.get("/v1/events/{token}", tags=['event'])
async def get_event_information(token: str) -> json:
    """
    Params: token:string
    {
    Background image: string,
    Title: string,
    Number of exercises: number,
    Difficulty: string,
    }
    """
    pass
