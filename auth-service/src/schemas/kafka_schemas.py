from pydantic import BaseModel


class UserInfoSchema(BaseModel):
    id: str
    email: str
    username: str
