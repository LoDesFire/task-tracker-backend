from fastapi import APIRouter

from app.api.admin.v1.routes import admin_v1_router
from app.api.auth.v1.routes import auth_v1_router
from app.api.user.v1.routes import user_v1_router

main_router = APIRouter(prefix="/api")

main_router.include_router(auth_v1_router)
main_router.include_router(user_v1_router)
main_router.include_router(admin_v1_router)
