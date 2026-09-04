import allure
import requests

from services.api_base import ApiBase
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_models import (
    CommentResponseModel,
    CommentsListResponseModel,
    CommentDeleteResponseModel
)
from services.comment.comment_payload import CommentPayload
from services.error_models import ErrorResponseModel


class ApiComment(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 30):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /posts/{post_id}/comments")
    def create_comment(self, post_id: int | str, payload: dict | None = None) -> CommentResponseModel:
        if payload is None:
            payload = CommentPayload.create_comment_payload()
        response = self.send_request(
            method="POST",
            url=self.endpoint.create_comment(post_id=post_id),
            json=payload
        )
        body = self._check_status_code(response, ok_statuses=[201])
        comment = CommentResponseModel.model_validate(body)
        assert comment.post_id == int(post_id)
        return comment

    @allure.step("GET == /posts/{post_id}/comments")
    def get_list_comments_by_post_id(self, post_id: int | str, page: int, per_page: int) -> CommentsListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments_by_post_id(post_id=post_id),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return CommentsListResponseModel(
            data=[CommentResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("GET == /comments?page=*&per_page=*")
    def get_list_comments(self, page: int, per_page: int) -> CommentsListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments(),
            params={"page": page, "per_page": per_page}
        )
        body = self._check_status_code(response, ok_statuses=[200])
        assert isinstance(body, list)
        return CommentsListResponseModel(
            data=[CommentResponseModel.model_validate(item) for item in body],
            **self._pagination_from_response(response)
        )

    @allure.step("DELETE == /comments/{comment_id}")
    def delete_comment(
            self,
            comment_id: int | str,
            expected_status_code: int = 204,
            allow_not_found: bool = False) -> CommentDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_comment(comment_id=comment_id)
        )
        if allow_not_found and response.status_code == 404:
            return None
        if expected_status_code == 204:
            self._check_status_code(response, ok_statuses=[204])
            assert response.content == b"", "DELETE 204 должен возвращать пустое body"
            return CommentDeleteResponseModel(id=int(comment_id))
        return self.error_from_response(response, expected_status_code)
