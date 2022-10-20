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
    timestamp_edited = Column(TIMESTAMP)


class Tokens(Base):
    __tablename__ = "tokens"

    token_id = Column(INTEGER, primary_key=True)
    token = Column(TINYTEXT)
    user_id = Column(
        ForeignKey("registration.user_id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    auth_level = Column(INTEGER)
