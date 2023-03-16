from fastapi import APIRouter
from api.routers.v1 import (
    account,
    challenge,
    dashboard,
    event,
    images,
    inbox,
    profile,
    trainer,
    workout,
    favorites,
)

router = APIRouter(prefix="/v1")

router.include_router(router=account.router)
router.include_router(router=challenge.router)
router.include_router(router=dashboard.router)
router.include_router(router=event.router)
router.include_router(router=images.router)
router.include_router(router=inbox.router)
router.include_router(router=profile.router)
router.include_router(router=trainer.router)
router.include_router(router=workout.router)
router.include_router(router=favorites.router)
