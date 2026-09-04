import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayloads


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.smoke
class TestPostSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET -> PUT -> GET -> DELETE -> GET 404")
    def test_post_smoke(self, created_user, created_post):
        with allure.step("Create user and post"):
            user = created_user()
            post = created_post(user_id=user.id)
            assert post.id > 0
            assert post.user_id == user.id
            assert post.title
            assert post.body

        with allure.step("Get created post"):
            got = self.api_post.get_post_by_id(post_id=post.id)
            assert got.id == post.id
            assert got.user_id == user.id
            assert got.title == post.title
            assert got.body == post.body

        with allure.step("Update post with PUT"):
            update_payload = PostPayloads.update_post_payload()
            updated = self.api_post.update_post(post_id=post.id, payload=update_payload)
            assert updated.id == post.id
            assert updated.user_id == user.id
            assert updated.title == update_payload["title"]
            assert updated.body == update_payload["body"]

        with allure.step("Get post after update"):
            got_after_update = self.api_post.get_post_by_id(post_id=post.id)
            assert got_after_update == updated

        with allure.step("Delete post"):
            deleted = self.api_post.delete_post(post_id=post.id)
            assert deleted.id == post.id
            assert deleted.status_code == 204

        with allure.step("Check post is absent"):
            error = self.api_post.get_post_by_id(post_id=post.id, expected_status_code=404)
            assert error.status_code == 404
