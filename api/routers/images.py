import json

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, insert, delete
from api.config import redis_client
import api.routers.functions.account as account_functions
import api.routers.models.account as account_models
from api.database.database import USERDATA_ENGINE
from api.database.functions import hashbrown, sqlalchemy_result
from api.database.models import Registration, Tokens, Blocks
from api.routers.functions.general import get_token_user_id
from fastapi.responses import FileResponse
import os
from api.database.functions import redis_decode

router = APIRouter()


@router.get("/v1/image/{image_id}", tags=["images"])
async def get_image(image_id: str) -> json:
    """get image copy"""
    image_route = await redis_client.get(image_id)
    image_route = redis_decode(bytes_encoded=image_route)
    return FileResponse("C:/Users/thear/Documents/GitHub/API/images/8/profile.jpeg")
