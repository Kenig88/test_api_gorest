import allure
import requests

from services.api_base import ApiBase
from services.error_models import ErrorResponseModel
from services.post.post_endpoints import PostEndpoints
from services.post.post_models import (
    PostResponseModel,
    PostListResponseModel,
    PostDeleteResponseModel
)
from services.post.post_payload import PostPayloads


class ApiPost(ApiBase):
    def __init__(
            self,
            http_session: requests.Session,
            endpoints: PostEndpoints,
            timeout: int = 15
    ):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /users/{user_id}/posts")
    def create_post(self, user_id: int | str, payload: dict | None = None) -> PostResponseModel:
        if payload is None:
            payload = PostPayloads.create_post_payload()

        response = self.send_request(
            method="POST",
            url=self.endpoint.create_post(user_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[201])
        post = PostResponseModel.model_validate(body)
        assert post.user_id == int(user_id)
        return post

    @allure.step("GET == /users{user_id}/posts")
    def get_list_posts_by_user_id(self, user_id: int | str, page: int, per_page: int) -> PostListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_posts_by_user_id(user_id),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return PostListResponseModel(
            data=[PostResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /posts?page=*&per_page=*")
    def get_list_posts(self, page: int, per_page: int) -> PostListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_posts(),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return PostListResponseModel(
            data=[PostResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /posts/{post_id}")
    def get_post_by_id(
            self, post_id: int | str,
            expected_status_code: int = 200
    ) -> PostResponseModel | ErrorResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_post_by_id(post_id)
        )
        if expected_status_code == 200:
            body = self._check_status_code(response, ok_statuses=[200])
            return PostResponseModel.model_validate(body)
        return self.error_from_response(response, expected_status_code)

    @allure.step("PUT == /posts/{post_id}")
    def update_post(self, post_id: int | str, payload: dict | None = None) -> PostResponseModel:
        if payload is None:
            payload = PostPayloads.update_post_payload()
        response = self.send_request(
            method="PUT",
            url=self.endpoint.update_post(post_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return PostResponseModel.model_validate(body)

    @allure.step("DELETE == /posts/{post_id}")
    def delete_post(
            self,
            post_id: int | str,
            expected_status_code: int = 204,
            allow_not_found: bool = False
    ) -> PostDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_post(post_id)
        )
        if allow_not_found and response.status_code == 404:
            return None
        if expected_status_code == 204:
            self._check_status_code(response, ok_statuses=[204])
            assert response.content == b"", "DELETE 204 должен возвращать пустое body"
            return PostDeleteResponseModel(id=int(post_id))
        return self.error_from_response(response, expected_status_code)
