from fastapi import APIRouter

from api.routers.v1.challenge import challenge

router = APIRouter(prefix="/challenge")
router.include_router(router=challenge.router)
