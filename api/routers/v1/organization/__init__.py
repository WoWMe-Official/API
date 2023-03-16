from fastapi import APIRouter

from api.routers.v1.organization import org, user

router = APIRouter(prefix="/organization")
router.include_router(router=org.router)
router.include_router(router=user.router)
