from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ValidationErrorItemModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    field: str
    message: str


class ErrorResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status_code: int
    message: str | None = None
    validation_errors: list[ValidationErrorItemModel] = Field(default_factory=list)
    raw_body: Any = None
