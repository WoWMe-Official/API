import datetime
from typing import List, Optional

from pydantic import BaseModel


class inbox_conversation_start(BaseModel):
    sendee: int
    subject_line: str
    content: str
