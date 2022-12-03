import json

from fastapi import APIRouter

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
