import datetime
from typing import List, Optional

from pydantic import BaseModel


class login_details(BaseModel):
    email: str
    password: str


class day(BaseModel):
    day: int
    start_time: datetime.datetime
    end_time: datetime.datetime


class socials(BaseModel):
    facebook: bool
    instagram: bool


class role(BaseModel):
    isTrainer: bool
    isUser: bool


class user_information(BaseModel):
    available_days: List[day]
    height_ft_in: Optional[int]
    weight_lb: Optional[int]
    height_cm: Optional[int]
    weight_kg: Optional[int]
    body_fat_percentage: Optional[int]
    fitness_level: Optional[int]
    fitness_goals: Optional[List[str]]


class trainer_information(BaseModel):
    social_security_number: Optional[str]
    rate: Optional[int]
    payment_method: Optional[str]
    specializations: Optional[List[str]]


class personal_information(BaseModel):
    email: str
    password: str
    phone: str
    first_name: str
    last_name: str
    birthdate: datetime.datetime
    about_you: str
    gender: int
    social: Optional[socials]


class signup(BaseModel):
    personal_information: personal_information
    role: role
    user_information: Optional[user_information]
    trainer_information: Optional[trainer_information]


class login_information(BaseModel):
    email: str
    password: str
