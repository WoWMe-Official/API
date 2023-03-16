from fastapi import APIRouter

from api.routers.v1.inbox import inbox

router = APIRouter(prefix="/inbox")
router.include_router(router=inbox.router)
