import json
import logging
from typing import Any, ClassVar

import allure
import requests

# Логгер для записи технических ошибок
logger = logging.getLogger(__name__)


class Helper:
    # Заголовки, значения которых нельзя показывать в Allure
    SENSITIVE_HEADERS: ClassVar[frozenset[str]] = frozenset(
        {"authorization", "proxy-authorization", "app-id"}
    )

    # Скрывает значения секретных заголовков символами ***
    def _mask_sensitive_headers(self, headers: Any) -> dict[str, str]:
        return {
            str(key): "***" if str(key).lower() in self.SENSITIVE_HEADERS else str(value)
            for key, value in dict(headers).items()
        }

    # Скрывает секретные значения, если они встретились в тексте
    def _mask_sensitive_values(self, text: str, headers: Any) -> str:
        masked_text = text

        for key, value in dict(headers).items():
            if str(key).lower() in self.SENSITIVE_HEADERS and value:
                masked_text = masked_text.replace(str(value), "***")

        return masked_text

    # Красиво форматирует тело запроса
    def _format_request_body(self, body: Any) -> str:
        if body is None:
            return "<empty>"

        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")

        if not isinstance(body, str):
            return str(body)

        try:
            return json.dumps(
                json.loads(body),
                indent=2,
                ensure_ascii=False,
            )
        except (TypeError, ValueError):
            return body

    # Красиво форматирует тело ответа API
    def _format_response_body(self, response: requests.Response) -> str:
        try:
            return json.dumps(
                response.json(),
                indent=2,
                ensure_ascii=False,
            )
        except ValueError:
            return response.text or "<empty>"

    # Добавляет Request и Response в Allure-отчёт
    def attach_response_safe(self, response: requests.Response) -> None:
        # Не добавляем один и тот же response повторно
        if getattr(response, "_allure_attached", False):
            return

        # Добавляем информацию о запросе
        try:
            request = response.request

            # Скрываем секретные заголовки
            headers = self._mask_sensitive_headers(request.headers)

            # Форматируем тело запроса
            request_body = self._format_request_body(request.body)

            # Скрываем секретные значения в теле
            request_body = self._mask_sensitive_values(
                request_body,
                request.headers,
            )

            allure.attach(
                (
                    f"{request.method} {request.url}\n\n"
                    f"Headers:\n"
                    f"{json.dumps(headers, indent=2, ensure_ascii=False)}\n\n"
                    f"Body:\n{request_body}"
                ),
                name="Request",
                attachment_type=allure.attachment_type.TEXT,
            )

        # Если Allure не смог добавить Request — пишем ошибку в лог
        except Exception:
            logger.debug(
                "Could not attach request to Allure",
                exc_info=True,
            )

        # Добавляем информацию об ответе
        try:
            response_headers = self._mask_sensitive_headers(
                response.headers
            )

            allure.attach(
                (
                    f"Status code: {response.status_code}\n"
                    f"Response time: "
                    f"{response.elapsed.total_seconds():.3f} sec\n\n"
                    f"Headers:\n"
                    f"{json.dumps(response_headers, indent=2, ensure_ascii=False)}\n\n"
                    f"Body:\n{self._format_response_body(response)}"
                ),
                name="Response",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Отмечаем, что этот response уже добавили в Allure
            response._allure_attached = True

        # Если Allure не смог добавить Response — пишем ошибку в лог
        except Exception:
            logger.debug(
                "Could not attach response to Allure",
                exc_info=True,
            )

    # Добавляет в Allure ошибку соединения/timeout
    def attach_transport_error_safe(
            self,
            method: str,
            url: str,
            timeout: Any,
            error: requests.RequestException,
    ) -> None:
        try:
            allure.attach(
                (
                    f"{method.upper()} {url}\n"
                    f"Timeout: {timeout!r}\n"
                    f"Error: {type(error).__name__}: {error}"
                ),
                name="Transport error",
                attachment_type=allure.attachment_type.TEXT,
            )

        # Даже ошибка Allure не должна ломать тест
        except Exception:
            logger.debug(
                "Could not attach transport error to Allure",
                exc_info=True,
            )
