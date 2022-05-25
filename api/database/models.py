from datetime import datetime

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


class Users(Base):
    __tablename__ = "users"

    user_id = Column(INTEGER, primary_key=True)
    login = Column(VARCHAR(64))
    password = Column(TINYTEXT)
    timestamp = Column(TIMESTAMP)


class UserChat(Base):
    __tablename__ = "user_chat"

    ID = Column(BigInteger, primary_key=True)
    timestamp = Column(TIMESTAMP)
    s_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    r_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    contains_image = Column(TINYINT)
    image_key = Column(TINYTEXT)
    chat = Column(TINYTEXT)


class UserImages(Base):
    __tablename__ = "user_images"

    ID = Column(INTEGER, primary_key=True)
    s_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    chat = Column(TINYINT)
    profile = Column(TINYINT)
    bio = Column(TINYINT)
    banner = Column(TINYINT)
    image_key = Column(TINYTEXT)
    image = Column(BLOB)
    size = Column(TINYINT)
    timestamp = Column(TIMESTAMP)


class UserInformation(Base):
    __tablename__ = "user_information"

    ID = Column(INTEGER, primary_key=True)
    user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    first_name = Column(TINYTEXT)
    middle_name = Column(TINYTEXT)
    last_name = Column(TINYTEXT)
    email = Column(VARCHAR(255), unique=True)
    phone = Column(VARCHAR(32), unique=True)
    birthday = Column(DATETIME)
    gender = Column(TINYINT)
    location = Column(TINYTEXT)
    timestamp = Column(TIMESTAMP)
    SSN = Column(VARCHAR(16), unique=True)


class UserRatingHistory(Base):
    __tablename__ = "user_rating_history"
    ID = Column(BigInteger, primary_key=True)
    timestamp = Column(TIMESTAMP)
    s_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    r_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    rating = Column(TINYINT)
    comment = Column(TINYTEXT)
    request_history_id = Column(BigInteger)


class UserStats(Base):
    __tablename__ = "user_stats"
    ID = Column(INTEGER, primary_key=True)
    user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    timestamp = Column(TIMESTAMP)
    height = Column(TINYINT)
    weight = Column(SMALLINT)
    experience = Column(TINYINT)
    fat_percentage = Column(TINYINT)
    fitness_level = Column(TINYINT)
    fitness_goals = Column(TINYINT)
    ava_dotw = Column(TINYINT)
    ava_hr_start = Column(TIME)
    ava_hr_end = Column(TIME)
    pricing_per_hour = Column(SMALLINT)


class UserToken(Base):
    __tablename__ = "user_token"
    ID = Column(INTEGER, primary_key=True)
    user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    auth_level = Column(TINYINT)
    token = Column(TINYTEXT)


class TrainerIdentificationInformation(Base):
    __tablename__ = "trainer_identification_information"
    ID = Column(INTEGER, primary_key=True)
    user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    content = Column(BLOB)
    content_type = Column(TINYINT)
    timestamp = Column(TIMESTAMP)


class TrainerAcceptionStatus(Base):
    __tablename__ = "trainer_acception_status"
    ID = Column(INTEGER, primary_key=True)
    user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    is_trainer = Column(TINYINT)
    is_pending = Column(TINYINT)
    timestamp = Column(TIMESTAMP)


class RequestHistory(Base):
    __tablename__ = "request_history"
    ID = Column(BigInteger, primary_key=True)

    s_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    r_user_id = Column(
        ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    timestamp_START = Column(TIMESTAMP)
    timestamp_DEAD = Column(TIMESTAMP)
    status = Column(TINYINT)
    price_per_hour = Column(INTEGER)
    timestamp_start_session = Column(TIMESTAMP)
    timestamp_end_session = Column(TIMESTAMP)
    fitness_categories = Column(INTEGER)
