import json

from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, status
import api.routers.models.challenge as challenge_models
from api.routers.functions.general import get_token_user_id

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


@router.post("/v1/challenge/{token}", tags=["challenge"])
async def start_challenge(
    token: str, challenge_details: challenge_models.challenge_details
) -> json:

    uuid = await get_token_user_id(token=token)

    return
