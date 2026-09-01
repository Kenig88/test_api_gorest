import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.smoke
class TestCommentSmoke(BaseTest):
    @allure.title("Smoke: CREATE -> LIST by post -> DELETE -> DELETE 404")
    def test_comment_smoke(self, created_user, created_post, created_comment):
        with allure.step("Create user, post and comment"):
            user = created_user()
            post = created_post(user_id=user.id)
            comment = created_comment(post_id=post.id)
            assert comment.id > 0
            assert comment.post_id == post.id
            assert comment.name
            assert comment.email
            assert comment.body

        with allure.step("Get comments by post and find created comment"):
            response = self.api_comment.get_list_comments_by_post_id(post_id=post.id, page=1, per_page=100)
            found = next((item for item in response.data if item.id == comment.id), None)
            assert found is not None
            assert found.id == comment.id
            assert found.post_id == post.id
            assert found.name == comment.name
            assert found.email == comment.email
            assert found.body == comment.body

        with allure.step("Delete comment"):
            deleted = self.api_comment.delete_comment(comment_id=comment.id)
            assert deleted.id == comment.id
            assert deleted.status_code == 204

        with allure.step("Check repeated delete returns 404"):
            error = self.api_comment.delete_comment(comment_id=comment.id, expected_status_code=404)
            assert error.status_code == 404
