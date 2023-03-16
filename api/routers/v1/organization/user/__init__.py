from fastapi import APIRouter

from api.routers.v1.organization.user import user

router = APIRouter(prefix="/user")
router.include_router(router=user.router)
