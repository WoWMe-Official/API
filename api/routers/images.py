import json

from fastapi import APIRouter
from fastapi.responses import FileResponse

from api.config import redis_client

router = APIRouter()


@router.get("/v1/image/{image_id}", tags=["images"])
async def get_image(image_id: str) -> json:
    """get image copy"""
    image_route = await redis_client.get(image_id)
    image_route = image_route.decode("utf-8")
    return FileResponse(image_route)
