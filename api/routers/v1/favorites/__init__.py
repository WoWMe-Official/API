from fastapi import APIRouter

from api.routers.v1.favorites import favorites

router = APIRouter(prefix="/favorites")
router.include_router(router=favorites.router)
