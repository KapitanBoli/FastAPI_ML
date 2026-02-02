from fastapi import APIRouter
from .user import router as user_api
from .auth import router as auth_api
from .video import router as video_api

router = APIRouter()
router.include_router(user_api, prefix="/user", tags=["User"])
router.include_router(auth_api, prefix="/auth", tags=["Auth"])
router.include_router(video_api, prefix="/video", tags=["Video"])
