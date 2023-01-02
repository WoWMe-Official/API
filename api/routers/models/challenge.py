import datetime
from typing import List, Optional

from pydantic import BaseModel


class day(BaseModel):
    day: int
    start_time: datetime.datetime
    end_time: datetime.datetime


class organization(BaseModel):
    name: str
    image_route: str
    distance: int


class leaderboard(BaseModel):
    name: str
    pace: int
    distance: int


class challenge_details(BaseModel):
    name: str
    background: str
    profile_route: str
    description: str
    start_date: day
    end_date: day
    distance: int
    reward: str
    organization: organization
    leaderboard: leaderboard
