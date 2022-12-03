import json

from fastapi import APIRouter
from sqlalchemy.sql.expression import select, update

router = APIRouter()


@router.get("/v1/events/{token}", tags=["event"])
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
