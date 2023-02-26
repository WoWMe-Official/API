import datetime
from typing import List, Optional

from pydantic import BaseModel


class event(BaseModel):
    uuid: int
    hash: Optional[str]
    background_image: str
    title: str
    description: str
    num_excercises: int
    difficulty: str


class edit_event(BaseModel):
    edit_background_image: str
    edit_title: str
    edit_description: str
    edit_num_excercises: int
    edit_difficulty: str
