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


@router.get("/v1/dashboard/{token}/{user_id}", tags=["dashboard"])
async def get_dashboard_information(token: str, user_id: str) -> json:
    """
    Params:
    {
    token:string,
    User id: number,
    }
    Returns:
    Wallet balance: number,
    Earnings total: number,
    Taxes total: number,
    Hours worked: number,
    Sessions worked: number,
    Categories assigned: number,
    Clients count: number,
    Clients profiles: array:string,
    Steps: number,
    Distance: number,
    }
    """
    pass
