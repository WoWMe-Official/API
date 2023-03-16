from fastapi import APIRouter

from api.routers.v1.organization.org import org

router = APIRouter(prefix="/org")
router.include_router(router=org.router)
