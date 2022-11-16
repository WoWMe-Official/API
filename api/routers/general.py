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


@router.get("/v1/profiles/{token}", tags=["profile"])
async def get_profile_information(token: str) -> json:
    """returns profile picture string, and user id"""


@router.get("/v1/trainers/{token}", tags=["trainers"])
async def get_trainer_information(token: str) -> json:
    """
    Background image: string,
    Title: string,
    Number of  exercises: number,
    Difficulty: string
    """


@router.get("/v1/events/{token}", tags=["events"])
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


@router.get("/v1/workout/{token}/{user_id}", tags=["workout"])
async def get_workout_plan(token: str, user_id: str) -> json:
    """
    Params:
    {
    Token: string,
    User id: number,
    }
    Returns:
    {
    Name: string,
    Rating: number,
    Number of workouts completed: number,
    Fitness level: string,
    Global stats: array: { title: string, stat: number },
    Workout plan: array: array: {workout: string, repts: string, weight: number}
    }
    """
    pass


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
