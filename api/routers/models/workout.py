import datetime
from typing import List, Optional

from pydantic import BaseModel


class stats(BaseModel):
    title: str
    hash: Optional[str]
    uuid: Optional[int]
    stat: int


class workout(BaseModel):
    hash: Optional[str]
    uuid: Optional[int]
    workout: str
    reps: int
    weight: float


class workout_plan(BaseModel):
    name: str
    uuid: Optional[int]
    rating: float
    workouts_completed: int
    fitness_level: str
    global_stats: List[stats]
    workout_plan: List[workout]
