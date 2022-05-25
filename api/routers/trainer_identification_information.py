# from datetime import datetime
# import json
# from typing import Optional
# from urllib.request import Request

# from api.database.functions import USERDATA_ENGINE, EngineType, sqlalchemy_result, verify_token
# from api.database.models import TrainerIdentificationInformation
# from fastapi import APIRouter, HTTPException, Query, status
# from pydantic import BaseModel
# from pydantic.fields import Field
# from pymysql import Timestamp
# from sqlalchemy import DATETIME, TIMESTAMP, func, select
# from sqlalchemy.dialects.mysql import Insert
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.orm import aliased
# from sqlalchemy.sql.expression import Select, select, insert

# router = APIRouter()


# class trainer_identification_information(BaseModel):
#     """
#     trainer_identification_information base model containing the types and content expected by the database
#     """


# @router.get(
#     "/V1/trainer-identification-information/",
#     tags=["trainer", "trainer identification information"],
# )
# async def get_trainer_identification_information(
#     token: str,
#     ID: Optional[int],
#     user_id: int,
#     content_type: Optional[int],
#     timestamp=Optional[datetime],
#     # content = Column(BLOB),
#     row_count: Optional[int] = Query(100, ge=1, le=1000),
#     page: Optional[int] = Query(1, ge=1),
# ) -> json:

#     table = TrainerIdentificationInformation
#     sql: Select = select(table)

#     sql = sql.limit(row_count).offset(row_count * (page - 1))

#     async with USERDATA_ENGINE.get_session() as session:
#         session: AsyncSession = session
#         async with session.begin():
#             data = await session.execute(sql)

#     data = sqlalchemy_result(data)
#     return data.rows2dict()


# @router.post(
#     "/V1/trainer-identification-information",
#     tags=["trainer", "trainer identification information"],
# )
# async def post_trainer_identification_status(
#     trainer_identification_information: trainer_identification_information,
# ) -> json:

#     values = trainer_identification_information.dict()
#     table = TrainerIdentificationInformation
#     sql = insert(table).values(values)
#     sql = sql.prefix_with("ignore")

#     async with USERDATA_ENGINE.get_session() as session:
#         session: AsyncSession = session
#         async with session.begin():
#             data = await session.execute(sql)

#     return {"ok": "ok"}
