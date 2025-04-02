from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.models.users import Users


class GetUserByIdSchema(BaseModel):
    id: int


class UsersSortingSchema(BaseModel):
    sort_by: Optional[list[str]] = Field(None)

    @field_validator("sort_by", mode="before")
    @classmethod
    def validate_sort_by(cls, values: list[str]) -> list[str]:
        """
        Validates the 'sort_by' parameter to ensure it contains only allowed fields
        and does not contain duplicates.
        """

        sortable_fields = Users.sortable_fields()
        cleaned_fields = {(f[1:] if f.startswith("-") else f) for f in values}

        if len(cleaned_fields) != len(values):
            raise ValueError("Duplicate sort fields are not allowed.")

        if not cleaned_fields.issubset(sortable_fields):
            raise ValueError(
                "Invalid sort field(s). The 'sort_by' parameter must contain "
                "only fields from the Users model. "
                "Available fields: {}".format(", ".join(sortable_fields))
            )
        return values


class UsersRoleFiltersSchema(BaseModel):
    is_admin: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_verified: Optional[bool] = Field(None)


class GetUsersSchema(UsersSortingSchema, UsersRoleFiltersSchema):
    pass


class UpdateUserByIdSchema(GetUserByIdSchema):
    email: EmailStr
    is_admin: bool
    is_active: bool
    is_verified: bool
    username: str


class DeleteUserByIdSchema(GetUserByIdSchema):
    pass
