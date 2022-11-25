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


@router.get("/v1/challenge/{token}/{challenge_id}", tags=["challenge"])
async def get_challenge_details(token: str, challenge_id: str) -> json:
    """
    Get Challenge Details
    Params:
    {
    Challenge id: number,
    Token: string,
    }

    Returns:
    {
    Name: string,
    Background: string,
    Profile picture: string,
    Description: string,
    Start date: string,
    End date: string,
    Distance: number,
    Reward: string,
    Organization: { name: string, image: string, distance: number}
    Leaderboard: array: {name: string, pace: number, distance: number}
    }
    """
    pass
