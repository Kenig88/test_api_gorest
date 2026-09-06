import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.negative
class TestUserNegative(BaseTest):
    # Заведомо несуществующий ID пользователя.
    # Используем его для проверки ответов 404.
    NONEXISTENT_USER_ID = 999999999999

    @allure.title("POST /users without token -> 401")
    def test_token_missing(self):
        # Отправляем запрос на создание пользователя без стандартных headers,
        # поэтому Authorization token в запрос не попадёт.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=UserPayloads.create_user_payload(),
            use_default_headers=False
        )

        # Без токена API должен вернуть 401 Unauthorized.
        self.api_user.assert_error_response(
            response,
            expected_status_code=401
        )

    @allure.title("POST /users with invalid token -> 401")
    def test_token_invalid(self):
        # Отправляем запрос с заведомо неправильным Bearer token.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            headers={"Authorization": "Bearer invalid_token"},
            json=UserPayloads.create_user_payload(),
            use_default_headers=False
        )

        # С неправильным токеном API должен вернуть 401 Unauthorized.
        self.api_user.assert_error_response(
            response,
            expected_status_code=401
        )

    @allure.title("Create user without required field '{field}' -> 422")
    @pytest.mark.parametrize(
        "field",
        [
            "name",
            "email",
            "gender",
            "status"
        ]
    )
    def test_create_without_required_field(self, field):
        # Создаём корректный payload пользователя.
        payload = UserPayloads.create_user_payload()

        # По очереди удаляем одно обязательное поле:
        # name, email, gender или status.
        payload.pop(field)

        # Пытаемся создать пользователя с неполными данными.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=payload
        )

        # API должен вернуть 422,
        # а ошибка должна относиться именно к удалённому полю.
        self.api_user.assert_error_response(
            response,
            expected_status_code=422,
            expected_field=field
        )

    @allure.title("Create user with invalid '{field}' -> 422")
    @pytest.mark.parametrize(
        "field, invalid_value",
        [
            ("gender", "unknown"),
            ("status", "unknown")
        ]
    )
    def test_create_with_invalid_enum(self, field, invalid_value):
        # Создаём корректный payload пользователя.
        payload = UserPayloads.create_user_payload()

        # Подменяем допустимое значение поля на недопустимое.
        # gender должен быть male/female,
        # status должен быть active/inactive.
        payload[field] = invalid_value

        # Отправляем запрос с неправильным значением поля.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=payload
        )

        # API должен вернуть 422
        # и указать проблемное поле в validation errors.
        self.api_user.assert_error_response(
            response,
            expected_status_code=422,
            expected_field=field
        )

    @allure.title("Create user with invalid email -> 422")
    def test_create_with_invalid_email(self):
        # Создаём корректный payload.
        payload = UserPayloads.create_user_payload()

        # Заменяем email на строку неправильного формата.
        payload["email"] = "invalid-email"

        # Пытаемся создать пользователя с неправильным email.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=payload
        )

        # API должен вернуть 422
        # и сообщить об ошибке поля email.
        self.api_user.assert_error_response(
            response,
            expected_status_code=422,
            expected_field="email"
        )

    @allure.title("Create user with duplicate email -> 422")
    def test_create_with_duplicate_email(self, created_user):
        # Создаём реального пользователя.
        existing_user = created_user()

        # Создаём новый корректный payload.
        payload = UserPayloads.create_user_payload()

        # Подставляем email уже существующего пользователя.
        payload["email"] = existing_user.email

        # Пытаемся создать второго пользователя с тем же email.
        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=payload
        )

        # Email должен быть уникальным,
        # поэтому API должен вернуть 422 с ошибкой поля email.
        self.api_user.assert_error_response(
            response,
            expected_status_code=422,
            expected_field="email"
        )

    @allure.title("Get nonexistent user -> 404")
    def test_get_nonexistent_user(self):
        # Пытаемся получить пользователя по ID,
        # которого гарантированно не существует.
        response = self.api_user.send_request(
            method="GET",
            url=self.api_user.endpoint.get_user_by_id(
                user_id=self.NONEXISTENT_USER_ID
            )
        )

        # Несуществующий пользователь должен вернуть 404 Not Found.
        self.api_user.assert_error_response(
            response,
            expected_status_code=404
        )

    @allure.title("Update nonexistent user -> 404")
    def test_update_nonexistent_user(self):
        # Пытаемся обновить пользователя,
        # которого не существует.
        response = self.api_user.send_request(
            method="PUT",
            url=self.api_user.endpoint.update_user(
                user_id=self.NONEXISTENT_USER_ID
            ),
            json=UserPayloads.update_user_payload()
        )

        # Обновление несуществующего ресурса должно вернуть 404.
        self.api_user.assert_error_response(
            response,
            expected_status_code=404
        )

    @allure.title("Delete nonexistent user -> 404")
    def test_delete_nonexistent_user(self):
        # Пытаемся удалить пользователя,
        # которого не существует.
        response = self.api_user.send_request(
            method="DELETE",
            url=self.api_user.endpoint.delete_user(
                user_id=self.NONEXISTENT_USER_ID
            )
        )

        # Удаление несуществующего ресурса должно вернуть 404.
        self.api_user.assert_error_response(
            response,
            expected_status_code=404
        )
