import allure
import requests

from services.api_base import ApiBase
from services.error_models import ErrorResponseModel
from services.user.user_endpoints import UserEndpoints
from services.user.user_models import (
    UserResponseModel,
    UserListResponseModel,
    UserDeleteResponseModel,
)
from services.user.user_payloads import UserPayloads


class ApiUser(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: UserEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /users")
    def create_user(self, payload: dict | None = None) -> UserResponseModel:
        if payload is None:
            payload = UserPayloads.create_user_payload()

        response = self.send_request(
            method="POST",
            url=self.endpoint.create_user(),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[201])
        return UserResponseModel.model_validate(body)

    @allure.step("GET == /users?page=*&per_page=*")
    def get_list_users(self, page: int, per_page: int) -> UserListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_users(),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list), {"expected": "list", "actual": type(body).__name__}

        return UserListResponseModel(
            data=[UserResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /users/{user_id}")
    def get_user_by_id(
            self,
            user_id: int | str,
            expected_status_code: int = 200
    ) -> UserResponseModel | ErrorResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_user_by_id(user_id)
        )

        if expected_status_code == 200:
            body = self._check_status_code(response, ok_statuses=[200])
            return UserResponseModel.model_validate(body)

        return self.error_from_response(response, expected_status_code)

    @allure.step("PUT == /users/{user_id}")
    def update_user(self, user_id: int | str, payload: dict | None = None) -> UserResponseModel:
        if payload is None:
            payload = UserPayloads.update_user_payload()

        response = self.send_request(
            method="PUT",
            url=self.endpoint.update_user(user_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return UserResponseModel.model_validate(body)

    @allure.step("DELETE == /users/{user_id}")
    def delete_user(
            self,
            user_id: int | str,
            expected_status_code: int = 204,
            allow_not_found: bool = False
    ) -> UserDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_user(user_id)
        )

        if allow_not_found and response.status_code == 404:
            return None

        if expected_status_code == 204:
            self._check_status_code(response, ok_statuses=[204])
            assert response.content == b"", "DELETE 204 должен возвращать пустое body"
            return UserDeleteResponseModel(id=int(user_id))

        return self.error_from_response(response, expected_status_code)
