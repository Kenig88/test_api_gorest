from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


# Модель одного пользователя
class UserResponseModel(BaseModel):
    # Лишние поля из ответа API просто игнорируем
    model_config = ConfigDict(extra="ignore")

    # id — целое число больше 0
    id: int = Field(strict=True, gt=0)

    # name — непустая строка
    name: str = Field(min_length=1)

    # email — строка, похожая на email
    email: str = Field(
        min_length=3,
        pattern=r"[^@\s]+@[^@\s]+$"
    )

    # gender может быть только male или female
    gender: Literal["male", "female"]

    # status может быть только active или inactive
    status: Literal["active", "inactive"]


# Модель данных для списка пользователей
class UserListResponseModel(BaseModel):
    # Лишние поля игнорируем
    model_config = ConfigDict(extra="ignore")

    # Количество данных, минимум 0
    data: list[UserResponseModel]

    # Общее количество пользователей, минимум 0
    total: int = Field(strict=True, ge=0)

    # Количество страниц, минимум 1
    pages: int = Field(strict=True, ge=1)

    # Текущая страница, минимум 1
    page: int = Field(strict=True, ge=1)

    # Лимит записей на странице: от 1 до 100
    limit: int = Field(strict=True, ge=1, le=100)


# Модель для удаления пользователя
class UserDeleteResponseModel(BaseModel):
    # Лишние поля запрещены
    model_config = ConfigDict(extra="forbid")

    # id удалённого пользователя
    id: int

    # Код успешного удаления по умолчанию — 204
    status_code: int = 204