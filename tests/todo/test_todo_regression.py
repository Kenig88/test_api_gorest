from datetime import datetime

import allure
import pytest

from config.base_test import BaseTest
from services.todo.todo_payload import TodoPayloads


@allure.epic("Administration")
@allure.feature("Todo")
@pytest.mark.regression
class TestTodoRegression(BaseTest):

    @allure.title("Create todo for user")
    def test_create_todo(self, created_user, created_todo):
        user = created_user()
        payload = TodoPayloads.create_todo_payload()
        todo = created_todo(user_id=user.id, overrides=payload)
        assert todo.user_id == user.id
        assert todo.title == payload["title"]
        assert todo.status == payload["status"]
        assert todo.due_on == datetime.fromisoformat(payload["due_on"])
        got = self.api_todo.get_todo_by_id(todo_id=todo.id)
        assert got == todo

    @allure.title("Get todos by user ID")
    def test_get_todos_by_user(self, created_user, created_todo):
        user = created_user()
        first = created_todo(user_id=user.id)
        second = created_todo(user_id=user.id)
        response = self.api_todo.get_list_todos_by_user_id(user_id=user.id, page=1, per_page=100)
        assert response.page == 1
        assert response.limit == 100
        assert all(todo.user_id == user.id for todo in response.data)
        todo_ids = {todo.id for todo in response.data}
        assert first.id in todo_ids
        assert second.id in todo_ids

    @allure.title("Get global todos list: page={page}, per_page={per_page}")
    @pytest.mark.parametrize(
        "page, per_page",
        [
            (1, 1),
            (1, 10),
            (1, 25),
            (2, 10),
        ]
    )
    def test_get_list_todos(self, page, per_page):
        response = self.api_todo.get_list_todos(page=page, per_page=per_page)
        assert len(response.data) <= per_page
        assert response.page == page
        assert response.limit == per_page
        assert response.total >= 0
        assert response.pages >= 0

    @allure.title("Get todo by ID")
    def test_get_todo_by_id(self, created_todo):
        todo = created_todo()
        got = self.api_todo.get_todo_by_id(todo_id=todo.id)
        assert got == todo

    @allure.title("Update todo")
    def test_update_todo(self, created_todo):
        todo = created_todo()
        update_payload = TodoPayloads.update_todo_payload()
        updated = self.api_todo.update_todo(todo_id=todo.id, payload=update_payload)
        assert updated.id == todo.id
        assert updated.user_id == todo.user_id
        assert updated.title == update_payload["title"]
        assert updated.due_on == datetime.fromisoformat(update_payload["due_on"])
        assert updated.status == update_payload["status"]
        assert updated.status != todo.status
        got = self.api_todo.get_todo_by_id(todo_id=todo.id)
        assert got == updated

    @allure.title("Delete todo")
    def test_delete_todo(self, created_todo):
        todo = created_todo()
        deleted = self.api_todo.delete_todo(todo_id=todo.id)
        assert deleted.id == todo.id
        error = self.api_todo.get_todo_by_id(todo_id=todo.id, expected_status_code=404)
        assert error.status_code == 404
