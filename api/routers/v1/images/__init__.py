from fastapi import APIRouter

from api.routers.v1.images import images

router = APIRouter(prefix="/image")
router.include_router(router=images.router)
