from sqlalchemy import DECIMAL, INTEGER, TIMESTAMP, VARCHAR, Column, ForeignKey, FLOAT
from sqlalchemy.dialects.mysql import TEXT, TINYINT, VARCHAR
from sqlalchemy.dialects.mysql.types import TINYTEXT
from sqlalchemy.ext.declarative import declarative_base

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
    account_type = Column(TINYINT)
    facebook = Column(TINYINT)
    instagram = Column(TINYINT)
    timestamp_edited = Column(TIMESTAMP)


class Relationships(Base):
    __tablename__ = "relationships"

    relationship_id = Column(INTEGER, primary_key=True)
    relationship_type = Column(TINYINT)
    user_id_1 = Column(INTEGER)
    user_id_2 = Column(INTEGER)
    pending_response = Column(TINYINT)
    target = Column(INTEGER)


class Ratings(Base):
    __tablename__ = "ratings"

    rating_id = Column(INTEGER, primary_key=True)
    rater = Column(INTEGER)
    rated = Column(INTEGER)
    rating = Column(TINYINT)


class AccountTypes(Base):
    __tablename__ = "account_types"

    ID = Column(TINYINT, primary_key=True)
    account_type = Column(TINYTEXT)


class UserInformation(Base):
    __tablename__ = "user_information"

    user_id = Column(INTEGER, primary_key=True)
    height_ft_in = Column(DECIMAL)
    weight_lb = Column(INTEGER)
    height_cm = Column(INTEGER)
    weight_kg = Column(INTEGER)
    body_fat_percentage = Column(INTEGER)
    fitness_level = Column(INTEGER)


class ChallengeDetailsDay(Base):
    __tablename__ = "challenge_details_day"

    ID = Column(INTEGER, primary_key=True)
    day_hash = Column(TEXT)
    day_id = Column(INTEGER)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    is_start = Column(INTEGER)


class Organization(Base):
    __tablename__ = "organization"
    ID = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    image_route = Column(TEXT)
    distance = Column(INTEGER)


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    ID = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False)
    pace = Column(INTEGER, nullable=False)
    distance = Column(INTEGER, nullable=False)


class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    name = Column(TEXT, nullable=False)
    background = Column(TEXT, nullable=False)
    profile_picture = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    start_date = Column(INTEGER, nullable=False)
    end_date = Column(INTEGER, nullable=False)
    distance = Column(INTEGER, nullable=False)
    reward = Column(TEXT, nullable=False)
    organization = Column(INTEGER, nullable=False)
    leaderboard = Column(INTEGER, nullable=False)


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


class TrainerStats(Base):
    __tablename__ = "trainer_stats"

    trainer_id = Column(INTEGER, primary_key=True)
    wallet_balance = Column(DECIMAL)
    earnings_total = Column(DECIMAL)
    taxes_total = Column(DECIMAL)
    hours_worked = Column(DECIMAL)
    sessions_worked = Column(INTEGER)
    categories_assigned = Column(INTEGER)
    client_count = Column(INTEGER)
    steps = Column(INTEGER)
    distance = Column(INTEGER)


class TrainerClientHistory(Base):
    __tablename__ = "trainer_client_history"

    session_id = Column(INTEGER, primary_key=True)
    trainer_id = Column(INTEGER)
    client_id = Column(INTEGER)
    timestamp = Column(TIMESTAMP)


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


class WorkoutPlan(Base):
    __tablename__ = "workout_plan"
    id = Column(INTEGER, primary_key=True)
    name = Column(TEXT, nullable=False)
    uuid = Column(INTEGER)
    rating = Column(FLOAT)
    workouts_completed = Column(INTEGER)
    fitness_level = Column(TEXT)


class Stats(Base):
    __tablename__ = "stats"
    id = Column(INTEGER, primary_key=True)
    uuid = Column(INTEGER)
    hash = Column(TEXT)
    title = Column(TEXT, nullable=False)
    stat = Column(INTEGER)


class Blocks(Base):
    __tablename__ = "blocks"
    id = Column(INTEGER, primary_key=True)
    blocker_id = Column(INTEGER)
    blocked_id = Column(INTEGER)


class Workout(Base):
    __tablename__ = "workout"
    id = Column(INTEGER, primary_key=True)
    uuid = Column(INTEGER)
    hash = Column(TEXT)
    workout = Column(TEXT, nullable=False)
    reps = Column(INTEGER)
    weight = Column(FLOAT)


class StatWorkoutHash(Base):
    __tablename__ = "stat_workout_hash"
    id = Column(INTEGER, primary_key=True)
    uuid = Column(INTEGER)
    stat = Column(TEXT, nullable=False)
    workout = Column(TEXT, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id = Column(INTEGER, primary_key=True)
    uuid = Column(INTEGER, nullable=False)
    hash = Column(TEXT, nullable=False)
    background_image = Column(TEXT, nullable=False)
    title = Column(TEXT, nullable=False)
    description = Column(TEXT, nullable=False)
    num_excercises = Column(INTEGER, nullable=False)
    difficulty = Column(TEXT, nullable=False)


class Inbox(Base):
    __tablename__ = "inbox"

    inbox_id = Column(INTEGER, primary_key=True, autoincrement=True)
    inbox_token = Column(INTEGER)
    timestamp = Column(TIMESTAMP)
    sender = Column(INTEGER, nullable=False)
    subject_line = Column(TEXT, nullable=False)
    content = Column(TEXT, nullable=False)
    message_edited = Column(INTEGER, nullable=False)


class Bcc(Base):
    __tablename__ = "bcc"

    bcc_id = Column(INTEGER, primary_key=True, autoincrement=True)
    inbox_token = Column(TEXT, nullable=False)
    uuid = Column(INTEGER, nullable=False)


class Cc(Base):
    __tablename__ = "cc"

    cc_id = Column(INTEGER, primary_key=True, autoincrement=True)
    inbox_token = Column(TEXT, nullable=False)
    uuid = Column(INTEGER, nullable=False)


class InboxPerms(Base):
    __tablename__ = "inbox_perms"
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    inbox_token = Column(TEXT, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    can_access = Column(INTEGER)
