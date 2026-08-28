import logging
from collections.abc import Sequence
from typing import Any

import requests

from services.error_models import ErrorResponseModel, ValidationErrorItemModel
from utils.helper import Helper

# Логгер для запросов и ошибок
logger = logging.getLogger(__name__)


# Базовый класс для работы с API.
# Наследуется от Helper, поэтому может использовать его методы для Allure.
class ApiBase(Helper):

    # Сохраняем HTTP-сессию и стандартный timeout
    def __init__(self, http_session: requests.Session, timeout: int = 15):
        self.http_session = http_session
        self.timeout = timeout

    # Получает JSON из ответа.
    # Если ответ не JSON — возвращает обычный текст.
    def _json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    # Отправляет HTTP-запрос
    def send_request(
            self,
            method: str,
            url: str,
            use_default_headers: bool = True,
            **kwargs: Any,
    ) -> requests.Response:

        # Если timeout не передали вручную,
        # используем стандартный timeout класса
        kwargs.setdefault("timeout", self.timeout)

        # Позволяет отправить запрос без стандартных headers сессии
        if not use_default_headers:
            headers = dict(kwargs.pop("headers", {}) or {})

            # Убираем стандартные заголовки для этого запроса
            headers.setdefault("Authorization", None)
            headers.setdefault("Accept", None)
            headers.setdefault("Content-Type", None)

            kwargs["headers"] = headers

        try:
            # Реально отправляем HTTP-запрос
            response = self.http_session.request(
                method=method,
                url=url,
                **kwargs,
            )

        # Обрабатываем сетевые ошибки, timeout и т.д.
        except requests.RequestException as error:
            logger.exception(
                "%s %s -> %s",
                method.upper(),
                url,
                type(error).__name__,
            )

            # Добавляем информацию об ошибке в Allure
            self.attach_transport_error_safe(
                method=method,
                url=url,
                timeout=kwargs.get("timeout"),
                error=error,
            )

            # Передаём ошибку дальше, чтобы тест не скрывал проблему
            raise

        # Добавляем Request и Response в Allure
        self.attach_response_safe(response)

        # Записываем метод, URL и status code в лог
        logger.info(
            "%s %s -> %s",
            response.request.method,
            response.url,
            response.status_code,
        )

        return response

    # Проверяет, что API вернул ожидаемый status code
    def _check_status_code(
            self,
            response: requests.Response,
            ok_statuses: Sequence[int],
    ) -> Any:

        # Получаем тело ответа
        body = self._json(response)

        # Проверяем status code
        assert response.status_code in ok_statuses, {
            "expected_statuses": list(ok_statuses),
            "actual_status": response.status_code,
            "url": str(response.url),
            "body": body,
        }

        return body

    # Получает информацию о пагинации из headers ответа
    def _pagination_from_response(
            self,
            response: requests.Response,
    ) -> dict[str, int]:

        # Связываем поля модели с headers GoRest
        header_names = {
            "total": "X-Pagination-Total",
            "pages": "X-Pagination-Pages",
            "page": "X-Pagination-Page",
            "limit": "X-Pagination-Limit",
        }

        result = {}

        # Получаем каждый pagination header
        for model_field, header_name in header_names.items():
            value = response.headers.get(header_name)

            # Проверяем, что header действительно присутствует
            assert value is not None, (
                f"В response отсутствует header {header_name}"
            )

            # Headers приходят строками, поэтому превращаем значение в int
            result[model_field] = int(value)

        return result

    # Преобразует ошибочный ответ API в ErrorResponseModel
    def error_from_response(
            self,
            response: requests.Response,
            expected_status_code: int,
    ) -> ErrorResponseModel:

        # Проверяем ожидаемый status code и получаем body
        body = self._check_status_code(
            response,
            ok_statuses=[expected_status_code],
        )

        # Если API вернул список ошибок валидации
        if isinstance(body, list):
            validation_errors = [
                ValidationErrorItemModel.model_validate(item)
                for item in body
            ]

            message = None

        # Если API вернул ошибку как словарь
        elif isinstance(body, dict):
            validation_errors = []

            # Пытаемся найти сообщение в message или error
            raw_message = body.get("message") or body.get("error")

            message = (
                str(raw_message)
                if raw_message is not None
                else None
            )

        # Если API вернул другой формат ошибки
        else:
            validation_errors = []
            message = str(body)

        # Возвращаем единую модель ошибки
        return ErrorResponseModel(
            status_code=response.status_code,
            message=message,
            validation_errors=validation_errors,
            raw_body=body,
        )

    # Проверяет ожидаемую ошибку API
    def assert_error_response(
            self,
            response: requests.Response,
            expected_status_code: int,
            expected_field: str | None = None,
    ) -> ErrorResponseModel:

        # Получаем разобранную ошибку
        error = self.error_from_response(
            response,
            expected_status_code,
        )

        # Если ожидаем ошибку конкретного поля
        if expected_field is not None:
            # Собираем названия всех полей с ошибками
            actual_fields = [
                item.field
                for item in error.validation_errors
            ]

            # Проверяем, что нужное поле действительно есть среди ошибок
            assert expected_field in actual_fields, {
                "expected_field": expected_field,
                "actual_fields": actual_fields,
                "body": error.raw_body,
            }

        return error
