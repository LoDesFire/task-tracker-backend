from fastapi import APIRouter

from web.api import files

main_router = APIRouter(prefix="/api")

main_router.include_router(files.router)
