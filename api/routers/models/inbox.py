import datetime
from typing import List, Optional

from pydantic import BaseModel


class inbox(BaseModel):
    inbox_id: int
    inbox_token: str
    timestamp: Optional[datetime.datetime]
    communication_id: int
    in_reply_to: Optional[int]
    sender: int
    sendee: int
    subject_line: str
    content: str


class bcc(BaseModel):
    bcc_id: Optional[int]
    inbox_token: str
    uuid: int


class cc(BaseModel):
    cc_id: Optional[int]
    inbox_token: str
    uuid: int


class inbox_conversation_start(BaseModel):
    sendee: int
    subject_line: str
    content: str
