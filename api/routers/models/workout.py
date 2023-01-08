import datetime
from typing import List, Optional

from pydantic import BaseModel


class stats(BaseModel):
    title: str
    stat: int


class workout(BaseModel):
    workout: str
    reps: int
    weight: float


class workout_plan(BaseModel):
    name: str
    rating: float
    workouts_completed: int
    fitness_level: str
    global_stats: List[stats]
    workout_plan: List[workout_plan]
