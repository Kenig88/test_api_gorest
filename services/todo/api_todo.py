import allure
import requests

from services.api_base import ApiBase
from services.error_models import ErrorResponseModel
from services.todo.todo_endpoints import TodoEndpoints
from services.todo.todo_models import (
    TodoResponseModel,
    TodoListResponseModel,
    TodoDeleteResponseModel
)
from services.todo.todo_payload import TodoPayloads


class ApiTodo(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: TodoEndpoints, timeout: int = 30):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /users/{user_id}/todos")
    def create_todo(self, user_id: int | str, payload: dict | None = None) -> TodoResponseModel:
        if payload is None:
            payload = TodoPayloads.create_todo_payload()
        response = self.send_request(
            method="POST",
            url=self.endpoint.create_todo(user_id=user_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[201])
        todo = TodoResponseModel.model_validate(body)
        assert todo.user_id == int(user_id)
        return todo

    @allure.step("GET == /users/{user_id}/todos")
    def get_list_todos_by_user_id(self, user_id: int | str, page: int, per_page: int) -> TodoListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_todos_by_user_id(user_id=user_id),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return TodoListResponseModel(
            data=[TodoResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /todos?page=*&per_page=*")
    def get_list_todos(self, page: int, per_page: int) -> TodoListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_todos(),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return TodoListResponseModel(
            data=[TodoResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /todos/{todo_id}")
    def get_todo_by_id(
            self,
            todo_id: int | str,
            expected_status_code: int = 200) -> TodoResponseModel | ErrorResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_todo_by_id(todo_id=todo_id)
        )
        if expected_status_code == 200:
            body = self._check_status_code(response, ok_statuses=[200])
            return TodoResponseModel.model_validate(body)
        return self.error_from_response(response, expected_status_code)

    @allure.step("PUT == /todos/{todo_id}")
    def update_todo(self, todo_id: int | str, payload: dict | None = None) -> TodoResponseModel:
        if payload is None:
            payload = TodoPayloads.update_todo_payload()
        response = self.send_request(
            method="PUT",
            url=self.endpoint.update_todo(todo_id=todo_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return TodoResponseModel.model_validate(body)

    @allure.step("DELETE == /todos/{todo_id}")
    def delete_todo(
            self,
            todo_id: int | str,
            expected_status_code: int = 204,
            allow_not_found: bool = False) -> TodoDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_todo(todo_id=todo_id)
        )
        if allow_not_found and response.status_code == 404:
            return None
        if expected_status_code == 204:
            self._check_status_code(response, ok_statuses=[204])
            assert response.content == b"", "DELETE 204 должен возвращать пустое body"
            return TodoDeleteResponseModel(id=int(todo_id))
        return self.error_from_response(response, expected_status_code)
