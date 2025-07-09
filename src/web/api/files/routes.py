from fastapi import APIRouter, Depends
from web.api import files
from web.api.files import projects, users

router = APIRouter(prefix="/files")

router.include_router(projects.router, tags=["Project Files"])
router.include_router(users.router, tags=["User Files"])
