from pydantic import BaseModel, ConfigDict, Field


class CommentResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(strict=True, gt=0)
    post_id: int = Field(strict=True, gt=0)
    name: str = Field(min_length=1)
    email: str = Field(min_length=3, pattern=r"^[^@\s]+@[^@\s]+$")
    body: str = Field(min_length=1)


class CommentsListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[CommentResponseModel]
    total: int = Field(strict=True, ge=0)
    pages: int = Field(strict=True, ge=0)
    page: int = Field(strict=True, ge=1)
    limit: int = Field(strict=True, ge=1, le=100)


class CommentDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    status_code: int = 204
