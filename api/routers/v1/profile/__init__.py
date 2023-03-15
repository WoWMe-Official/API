from fastapi import APIRouter

from api.routers.v1.profile import profile

router = APIRouter(prefix="/profile")
router.include_router(router=profile.router)
