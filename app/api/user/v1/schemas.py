from typing import Optional

from pydantic import BaseModel, EmailStr


class UpdateUserSchema(BaseModel):
    email: Optional[EmailStr]  # need email verification
    username: Optional[str]
    password: Optional[str]
