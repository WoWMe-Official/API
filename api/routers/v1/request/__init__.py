from fastapi import APIRouter

from api.routers.v1.request import requests

router = APIRouter(prefix="/requests")
router.include_router(router=requests.router)
