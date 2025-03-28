from fastapi import APIRouter

user_v1_router = APIRouter(prefix="/user", tags=["User Actions"])


@user_v1_router.put("/")
def update_user(
    # get user dependency
):
    pass


@user_v1_router.get("/")
def get_user(
    # get user dependency
):
    pass


@user_v1_router.delete("/")
def delete_user(
    # get user dependency
):
    pass
