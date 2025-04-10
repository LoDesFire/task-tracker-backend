from fastapi import APIRouter
from fastapi.params import Depends

from src.helpers.jwt_helper import JWTTokenPayload
from src.web.dependencies.auth_dependency import auth_dependency

user_v1_router = APIRouter(prefix="/user", tags=["User Actions"])


@user_v1_router.put("/")
def update_user(auth_context: JWTTokenPayload = Depends(auth_dependency)):
    pass


@user_v1_router.get("/")
def get_user(auth_context: JWTTokenPayload = Depends(auth_dependency)):
    pass


@user_v1_router.delete("/")
def delete_user(auth_context: JWTTokenPayload = Depends(auth_dependency)):
    pass
