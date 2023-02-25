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


### edit models


class edit_personal_details(BaseModel):
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    birthdate: Optional[datetime.datetime]
    about_you: Optional[str]
    gender: Optional[int]
    social: Optional[socials]


class edit_role(BaseModel):
    isTrainer: Optional[bool]
    isUser: Optional[bool]


class edit_user_information(BaseModel):
    available_days: Optional[List[day]]
    height_ft_in: Optional[int]
    weight_lb: Optional[int]
    height_cm: Optional[int]
    weight_kg: Optional[int]
    body_fat_percentage: Optional[int]
    fitness_level: Optional[int]
    fitness_goals: Optional[List[str]]


class edit_trainer_information(BaseModel):
    social_security_number: Optional[str]
    rate: Optional[int]
    payment_method: Optional[str]
    specializations: Optional[List[str]]


class edit_account_details(BaseModel):
    edit_personal_details: Optional[edit_personal_details]
    edit_role: Optional[edit_role]
    edit_user_information: Optional[edit_user_information]
    edit_trainer_information: Optional[edit_trainer_information]
