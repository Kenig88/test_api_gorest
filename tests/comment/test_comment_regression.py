import allure
import pytest

from config.base_test import BaseTest
from services.comment.comment_payload import CommentPayload


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.regression
class TestCommentRegression(BaseTest):

    @allure.title("Create comment for post")
    def test_create_comment(self, created_post, created_comment):
        post = created_post()
        payload = CommentPayload.create_comment_payload()
        comment = created_comment(post_id=post.id, overrides=payload)
        assert comment.post_id == post.id
        assert comment.name == payload["name"]
        assert comment.email == payload["email"]
        assert comment.body == payload["body"]
        response = self.api_comment.get_list_comments_by_post_id(post_id=post.id, page=1, per_page=100)
        assert any(item == comment for item in response.data)

    @allure.title("Get comments by post ID")
    def test_get_comments_by_post(self, created_post, created_comment):
        post = created_post()
        first = created_comment(post_id=post.id)
        second = created_comment(post_id=post.id)
        response = self.api_comment.get_list_comments_by_post_id(post_id=post.id, page=1, per_page=100)
        assert response.page == 1
        assert response.limit == 100
        assert all(comment.post_id == post.id for comment in response.data)
        comment_ids = {comment.id for comment in response.data}
        assert first.id in comment_ids
        assert second.id in comment_ids

    @allure.title("Get global comments: page={page}, per_page={per_page}")
    @pytest.mark.parametrize(
        "page, per_page",
        [
            (1, 1),
            (1, 10),
            (1, 25),
            (2, 10),
        ]
    )
    def test_get_list_comments(self, page, per_page):
        response = self.api_comment.get_list_comments(page=page, per_page=per_page)
        assert len(response.data) <= per_page
        assert response.page == page
        assert response.limit == per_page
        assert response.total >= 0
        assert response.pages >= 0

    @allure.title("Delete comment")
    def test_delete_comment(self, created_post, created_comment):
        post = created_post()
        comment = created_comment(post_id=post.id)
        deleted = self.api_comment.delete_comment(comment_id=comment.id)
        assert deleted.id == comment.id
        response = self.api_comment.get_list_comments_by_post_id(post_id=post.id, page=1, per_page=100)
        assert all(item.id != comment.id for item in response.data)
