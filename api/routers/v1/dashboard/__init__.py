from fastapi import APIRouter

from api.routers.v1.dashboard import dashboard

router = APIRouter(prefix="/dashboard")
router.include_router(router=dashboard.router)
