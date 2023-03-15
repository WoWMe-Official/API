from fastapi import APIRouter

from api.routers.v1.trainer import trainer

router = APIRouter(prefix="/trainer")
router.include_router(router=trainer.router)
