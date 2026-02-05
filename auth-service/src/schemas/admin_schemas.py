from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from src.helpers.schema_helpers import add_metadata_to_fields
from src.models.users import Users
from src.schemas.user_schemas import UsersIDType


class UsersSortingAdminSchema(BaseModel):
    sort_by: list[str] = Field(default_factory=list)

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


@add_metadata_to_fields(group="filters")
class UsersRoleFiltersAdminSchema(BaseModel):
    is_admin: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_verified: Optional[bool] = Field(None)
    id: Optional[UsersIDType] = Field(None)
    email: Optional[EmailStr] = Field(None)
    username: Optional[str] = Field(None)


class PaginationFiltersSchema(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(5, ge=1, le=100)


class GetUsersAdminSchema(
    UsersSortingAdminSchema,
    UsersRoleFiltersAdminSchema,
    PaginationFiltersSchema,
):
    """GetUsersAdminSchema"""

    def filters(self) -> dict[str, Any]:
        model_fields = self.model_dump(exclude_none=True)
        filters = {}
        for field_name, field_info in self.model_fields.items():
            if (
                isinstance(field_info.json_schema_extra, dict)
                and field_info.json_schema_extra.get("group", None) == "filters"
                and model_fields.get(field_name, None) is not None
            ):
                filters[field_name] = model_fields[field_name]

        return filters


class UpdateUserAdminSchema(BaseModel):
    email: Optional[EmailStr] = Field(None)
    is_admin: Optional[bool] = Field(None)
    is_active: Optional[bool] = Field(None)
    is_verified: Optional[bool] = Field(None)
    username: Optional[str] = Field(None)

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        for field_name, field_val in self.model_dump().items():
            if field_val is not None:
                return self

        raise ValueError("Must have at least one field")


class OutputUserAdminSchema(BaseModel):
    id: UsersIDType
    email: EmailStr
    username: str
    is_admin: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class OutputUsersAdminSchema(BaseModel):
    users: list[OutputUserAdminSchema]
    current_page: int
    total_pages: int
    total_items: int


class UserIdAdminSchema(BaseModel):
    id: UsersIDType
