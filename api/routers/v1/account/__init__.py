from fastapi import APIRouter

from api.routers.v1.account import account

router = APIRouter(prefix="/account")
router.include_router(router=account.router)
