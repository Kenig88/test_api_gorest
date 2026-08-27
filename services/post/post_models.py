from pydantic import BaseModel, ConfigDict, Field


class PostResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(strict=True, gt=0)
    user_id: int = Field(strict=True, gt=0)
    title: str = Field(min_length=1)
    body: str = Field(min_length=1)


class PostListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[PostResponseModel]
    total: int = Field(strict=True, ge=0)
    pages: int = Field(strict=True, ge=0)
    page: int = Field(strict=True, ge=1)
    limit: int = Field(strict=True, ge=1, le=100)


class PostDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    status_code: int = 204
