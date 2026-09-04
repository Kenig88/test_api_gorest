import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayloads


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.regression
class TestPostRegression(BaseTest):

    @allure.title("Create post for user")
    def test_create_post(self, created_user, created_post):
        user = created_user()
        payload = PostPayloads.create_post_payload()
        post = created_post(user_id=user.id, overrides=payload)
        assert post.user_id == user.id
        assert post.title == payload["title"]
        assert post.body == payload["body"]
        got = self.api_post.get_post_by_id(post.id)
        assert got == post

    @allure.title("Get posts by user ID")
    def test_get_posts_by_user(self, created_user, created_post):
        user = created_user()
        created = created_post(user_id=user.id)
        response = self.api_post.get_list_posts_by_user_id(user_id=user.id, page=1, per_page=100)
        assert all(post.user_id == user.id for post in response.data)
        assert any(post.id == created.id for post in response.data)

    @allure.title("Get global posts list: page={page}, per_page={per_page}")
    @pytest.mark.parametrize(
        "page, per_page",
        [
            (1, 1),
            (1, 10),
            (1, 25),
            (2, 10),
        ],
    )
    def test_get_list_posts(self, page, per_page):
        response = self.api_post.get_list_posts(
            page=page,
            per_page=per_page
        )
        assert len(response.data) <= per_page
        assert response.page == page
        assert response.limit == per_page
        assert response.total >= 0
        assert response.pages >= 0

    @allure.title("Get created post by ID")
    def test_get_post_by_id(self, created_post):
        post = created_post()
        got = self.api_post.get_post_by_id(post.id)
        assert got == post

    @allure.step("Update post")
    def test_update_post(self, created_post):
        post = created_post()
        update_payload = PostPayloads.update_post_payload()
        updated = self.api_post.update_post(post_id=post.id, payload=update_payload)
        assert updated.id == post.id
        assert updated.user_id == post.user_id
        assert updated.title == update_payload["title"]
        assert updated.body == update_payload["body"]
        got = self.api_post.get_post_by_id(post_id=post.id)
        assert got == updated

    @allure.title("Delete post")
    def test_delete_post(self, created_post):
        post = created_post()
        deleted = self.api_post.delete_post(post.id)
        assert deleted.id == post.id
        error = self.api_post.get_post_by_id(post_id=post.id, expected_status_code=404)
        assert error.status_code == 404
