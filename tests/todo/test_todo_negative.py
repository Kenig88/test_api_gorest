import allure
import pytest

from config.base_test import BaseTest
from services.todo.todo_payloads import TodoPayloads


@allure.epic("Administration")
@allure.feature("Todo")
@pytest.mark.negative
class TestTodoNegative(BaseTest):
    NONEXISTENT_USER_ID = 999999999999
    NONEXISTENT_TODO_ID = 999999999999

    @allure.title("POST /users/{user_id}/todos without token -> 401")
    def test_token_missing(self, created_user):
        user = created_user()
        response = self.api_todo.send_request(
            method="POST",
            url=self.api_todo.endpoint.create_todo(user_id=user.id),
            json=TodoPayloads.create_todo_payload(),
            use_default_headers=False
        )
        self.api_todo.assert_error_response(response, expected_status_code=401)

    @allure.title("Create todo without required field '{field}' -> 422")
    @pytest.mark.parametrize(
        "field",
        [
            "title",
            "status"]
    )
    def test_create_without_required_field(self, created_user, field):
        user = created_user()
        payload = TodoPayloads.create_todo_payload()
        payload.pop(field)
        response = self.api_todo.send_request(
            method="POST",
            url=self.api_todo.endpoint.create_todo(user_id=user.id),
            json=payload
        )
        self.api_todo.assert_error_response(response, expected_status_code=422, expected_field=field)

    @allure.title("Create todo with invalid status -> 422")
    def test_create_with_invalid_status(self, created_user):
        user = created_user()
        payload = TodoPayloads.create_todo_payload()
        payload["status"] = "unknown"
        response = self.api_todo.send_request(
            method="POST",
            url=self.api_todo.endpoint.create_todo(user_id=user.id),
            json=payload
        )
        self.api_todo.assert_error_response(response, expected_status_code=422, expected_field="status")

    @allure.title("Create todo for nonexistent user -> 422")
    def test_create_todo_for_nonexistent_user(self):
        response = self.api_todo.send_request(
            method="POST",
            url=self.api_todo.endpoint.create_todo(user_id=self.NONEXISTENT_USER_ID),
            json=TodoPayloads.create_todo_payload()
        )
        self.api_todo.assert_error_response(response, expected_status_code=422, expected_field="user")

    @allure.title("Get nonexistent todo -> 404")
    def test_get_nonexistent_todo(self):
        response = self.api_todo.send_request(
            method="GET",
            url=self.api_todo.endpoint.get_todo_by_id(todo_id=self.NONEXISTENT_TODO_ID)
        )
        self.api_todo.assert_error_response(response, expected_status_code=404)

    @allure.title("Update nonexistent todo -> 404")
    def test_update_nonexistent_todo(self):
        response = self.api_todo.send_request(
            method="PUT",
            url=self.api_todo.endpoint.update_todo(todo_id=self.NONEXISTENT_TODO_ID),
            json=TodoPayloads.update_todo_payload()
        )
        self.api_todo.assert_error_response(response, expected_status_code=404)

    @allure.title("Delete nonexistent todo -> 404")
    def test_delete_nonexistent_todo(self):
        response = self.api_todo.send_request(
            method="DELETE",
            url=self.api_todo.endpoint.delete_todo(todo_id=self.NONEXISTENT_TODO_ID)
        )
        self.api_todo.assert_error_response(response, expected_status_code=404)
