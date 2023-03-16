from fastapi import APIRouter

from api.routers.v1.event import event

router = APIRouter(prefix="/events")
router.include_router(router=event.router)
