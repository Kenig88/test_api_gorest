import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payloads import PostPayloads


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.negative
class TestPostNegative(BaseTest):
    NONEXISTENT_USER_ID = 999999999999
    NONEXISTENT_POST_ID = 999999999999

    @allure.title("POST /users/{user_id}/posts without token -> 401")
    def test_token_missing(self, created_user):
        user = created_user()
        response = self.api_post.send_request(
            method="POST",
            url=self.api_post.endpoint.create_post(user_id=user.id),
            json=PostPayloads.create_post_payload(),
            use_default_headers=False
        )
        self.api_post.assert_error_response(response, expected_status_code=401)

    @allure.title("Create post without required field '{field}' -> 422")
    @pytest.mark.parametrize(
        "field",
        [
            "title",
            "body"
        ]
    )
    def test_create_without_required_field(self, created_user, field):
        user = created_user()
        payload = PostPayloads.create_post_payload()
        payload.pop(field)
        response = self.api_post.send_request(
            method="POST",
            url=self.api_post.endpoint.create_post(user_id=user.id),
            json=payload
        )
        self.api_post.assert_error_response(response, expected_status_code=422, expected_field=field)

    @allure.title("Create post for nonexistent user -> 422")
    def test_create_post_for_nonexistent_user(self):
        response = self.api_post.send_request(
            method="POST",
            url=self.api_post.endpoint.create_post(user_id=self.NONEXISTENT_USER_ID),
            json=PostPayloads.create_post_payload()
        )
        self.api_post.assert_error_response(response, expected_status_code=422, expected_field="user")

    @allure.title("Get nonexistent post -> 404")
    def test_get_nonexistent_post(self):
        response = self.api_post.send_request(
            method="GET",
            url=self.api_post.endpoint.get_post_by_id(post_id=self.NONEXISTENT_POST_ID)
        )
        self.api_post.assert_error_response(response, expected_status_code=404)

    @allure.title("Update nonexistent post -> 404")
    def test_update_nonexistent_post(self):
        response = self.api_post.send_request(
            method="PUT",
            url=self.api_post.endpoint.update_post(post_id=self.NONEXISTENT_POST_ID),
            json=PostPayloads.update_post_payload()
        )
        self.api_post.assert_error_response(response, expected_status_code=404)

    @allure.title("Delete nonexistent post -> 404")
    def test_delete_nonexistent_post(self):
        response = self.api_post.send_request(
            method="DELETE",
            url=self.api_post.endpoint.delete_post(post_id=self.NONEXISTENT_POST_ID)
        )
        self.api_post.assert_error_response(response, expected_status_code=404)
