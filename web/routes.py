from fastapi import APIRouter

from web.api import admin_v1_router, auth_v1_router, user_v1_router

main_router = APIRouter(prefix="/api")

main_router.include_router(auth_v1_router)
main_router.include_router(user_v1_router)
main_router.include_router(admin_v1_router)
