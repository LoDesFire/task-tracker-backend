from fastapi import APIRouter
from src.web.api import statistics
main_router = APIRouter()

main_router.include_router(statistics.router, tags=["statistics"])