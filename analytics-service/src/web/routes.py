from fastapi import APIRouter
from web.api import statistics
main_router = APIRouter()

main_router.include_router(statistics.router, tags=["statistics"])