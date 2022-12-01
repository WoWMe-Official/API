from datetime import datetime
from enum import unique

from numpy import integer
from sqlalchemy import (
    BLOB,
    DATETIME,
    INTEGER,
    SMALLINT,
    TIME,
    TIMESTAMP,
    VARCHAR,
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    column,
    text,
)
from sqlalchemy.dialects.mysql import TEXT, TINYINT, VARCHAR
from sqlalchemy.dialects.mysql.types import TINYTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# generated with sqlacodegen
Base = declarative_base()
metadata = Base.metadata


class Registration(Base):
    __tablename__ = "registration"

    user_id = Column(INTEGER, primary_key=True)
    email = Column(VARCHAR(320))  # max email length
    password = Column(TINYTEXT)
    timestamp_created = Column(
        TIMESTAMP,
    )
    phone = Column(TINYTEXT)
    first_name = Column(TINYTEXT)
    last_name = Column(TINYTEXT)
    birthdate = Column(TIMESTAMP)
    about_you = Column(TEXT)
    gender = Column(TINYINT)
    facebook = Column(TINYINT)
    instagram = Column(TINYINT)
    timestamp_edited = Column(TIMESTAMP)


class UserInformation(Base):
    __tablename__ = "user_information"

    user_id = Column(INTEGER, primary_key=True)
    height = Column(INTEGER)
    weight = Column(INTEGER)
    body_fat_percentage = Column(INTEGER)
    fitness_level = Column(INTEGER)


class Genders(Base):
    __tablename__ = "genders"

    ID = Column(INTEGER, primary_key=True)
    gender = Column(TINYTEXT)


class FitnessLevel(Base):
    __tablename__ = "fitness_level"

    level = Column(INTEGER, primary_key=True)
    description = Column(TINYTEXT)


class FitnessGoals(Base):
    __tablename__ = "fitness_goals"

    ID = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER)
    goal = Column(TINYTEXT)


class AvailableDays(Base):
    __tablename__ = "available_days"

    ID = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER)
    day = Column(TINYTEXT)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)


class TrainerInformation(Base):
    __tablename__ = "trainer_information"

    user_id = Column(INTEGER, primary_key=True)
    social_security_number = Column(TINYTEXT)
    identification = Column(TINYTEXT)
    rate = Column(INTEGER)
    payment_method = Column(TINYTEXT)
    certification_photo = Column(TINYTEXT)


class Specializations(Base):
    __tablename__ = "specializations"

    ID = Column(INTEGER, primary_key=True)
    user_id = Column(INTEGER)
    specialization = Column(TINYTEXT)


class Tokens(Base):
    __tablename__ = "tokens"

    token_id = Column(INTEGER, primary_key=True)
    token = Column(TINYTEXT)
    user_id = Column(
        ForeignKey("registration.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    auth_level = Column(INTEGER)
