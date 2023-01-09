import datetime
from typing import List, Optional

from pydantic import BaseModel


class event(BaseModel):
    uuid: int
    hash: Optional[str]
    background_image: str
    title: str
    num_excercises: int
    difficulty: str
