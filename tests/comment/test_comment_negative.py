import allure
import pytest

from config.base_test import BaseTest
from services.comment.comment_payload import CommentPayload


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.negative
class TestCommentNegative(BaseTest):
    NONEXISTENT_POST_ID = 999999999999
    NONEXISTENT_COMMENT_ID = 999999999999

    @allure.title("POST /posts/{post_id}/comments without token -> 401")
    def test_token_missing(self, created_post):
        post = created_post()
        response = self.api_comment.send_request(
            method="POST",
            url=self.api_comment.endpoint.create_comment(post_id=post.id),
            json=CommentPayload.create_comment_payload(),
            use_default_headers=False
        )
        self.api_comment.assert_error_response(response, expected_status_code=401)

    @allure.title("Create comment without required field '{field}' -> 422")
    @pytest.mark.parametrize(
        "field",
        [
            "name",
            "email",
            "body"
        ]
    )
    def test_create_without_required_field(self, created_post, field):
        post = created_post()
        payload = CommentPayload.create_comment_payload()
        payload.pop(field)
        response = self.api_comment.send_request(
            method="POST",
            url=self.api_comment.endpoint.create_comment(post_id=post.id),
            json=payload
        )
        self.api_comment.assert_error_response(response, expected_status_code=422, expected_field=field)

    @allure.title("Create comment with invalid email -> 422")
    def test_create_with_invalid_email(self, created_post):
        post = created_post()
        payload = CommentPayload.create_comment_payload()
        payload["email"] = "invalid-email"
        response = self.api_comment.send_request(
            method="POST",
            url=self.api_comment.endpoint.create_comment(post_id=post.id),
            json=payload
        )
        self.api_comment.assert_error_response(response, expected_status_code=422, expected_field="email")

    @allure.title("Create comment for nonexistent post -> 422")
    def test_create_comment_for_nonexistent_post(self):
        payload = CommentPayload.create_comment_payload()
        response = self.api_comment.send_request(
            method="POST",
            url=self.api_comment.endpoint.create_comment(post_id=self.NONEXISTENT_POST_ID),
            json=payload
        )
        self.api_comment.assert_error_response(response, expected_status_code=422, expected_field="post")

    @allure.title("Delete nonexistent comment -> 404")
    def test_delete_nonexistent_comment(self):
        response = self.api_comment.send_request(
            method="DELETE",
            url=self.api_comment.endpoint.delete_comment(
                self.NONEXISTENT_COMMENT_ID
            )
        )
        self.api_comment.assert_error_response(response, expected_status_code=404)
