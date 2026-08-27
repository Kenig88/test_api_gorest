from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(strict=True, gt=0)
    name: str = Field(min_length=1)
    email: str = Field(min_length=3, pattern=r"[^@\s]+@[^@\s]+$")
    gender: Literal["male", "female"]
    status: Literal["active", "inactive"]


class UserListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: int = Field(strict=True, ge=0)
    total: int = Field(strict=True, ge=0)
    pages: int = Field(strict=True, ge=1)
    page: int = Field(strict=True, ge=1)
    limit: int = Field(strict=True, ge=1, le=100)


class UserDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    status_code: int = 204
