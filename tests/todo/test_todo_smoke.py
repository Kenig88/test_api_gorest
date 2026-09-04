from datetime import datetime

import allure
import pytest

from config.base_test import BaseTest
from services.todo.todo_payload import TodoPayloads


@allure.epic("Administration")
@allure.feature("Todo")
@pytest.mark.smoke
class TestTodoSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET -> PUT -> GET -> DELETE -> GET 404")
    def test_todo_smoke(self, created_user, created_todo):
        with allure.step("Create user and todo"):
            user = created_user()
            todo = created_todo(user_id=user.id)
            assert todo.id > 0
            assert todo.user_id == user.id
            assert todo.title
            assert todo.due_on
            assert todo.status == "pending"

        with allure.step("Get created todo"):
            got = self.api_todo.get_todo_by_id(todo_id=todo.id)
            assert got.id == todo.id
            assert got.user_id == user.id
            assert got.title == todo.title
            assert got.due_on == todo.due_on
            assert got.status == todo.status

        with allure.step("Update todo with PUT"):
            update_payload = TodoPayloads.update_todo_payload()
            updated = self.api_todo.update_todo(todo_id=todo.id, payload=update_payload)
            assert updated.id == todo.id
            assert updated.user_id == user.id
            assert updated.title == update_payload["title"]
            assert updated.status == update_payload["status"]
            assert updated.due_on == datetime.fromisoformat(update_payload["due_on"])

        with allure.step("Get todo after update"):
            got_after_update = self.api_todo.get_todo_by_id(todo_id=todo.id)
            assert got_after_update == updated

        with allure.step("Delete todo"):
            deleted = self.api_todo.delete_todo(todo_id=todo.id)
            assert deleted.id == todo.id
            assert deleted.status_code == 204

        with allure.step("Check todo is absent"):
            error = self.api_todo.get_todo_by_id(todo_id=todo.id, expected_status_code=404)
            assert error.status_code == 404
