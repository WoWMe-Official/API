from fastapi import APIRouter

from api.routers.v1.workout import workout

router = APIRouter(prefix="/workout")
router.include_router(router=workout.router)
