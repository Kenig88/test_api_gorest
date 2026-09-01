import pytest

from services.user.api_user import ApiUser
from services.post.api_post import ApiPost
from services.comment.api_comment import ApiComment
from services.todo.api_todo import ApiTodo


class BaseTest:
    api_user: ApiUser
    api_post: ApiPost
    api_comment: ApiComment
    api_todo: ApiTodo

    @pytest.fixture(autouse=True)
    def setup_apis(self, api_user, api_post, api_comment, api_todo):
        self.api_user = api_user
        self.api_post = api_post
        self.api_comment = api_comment
        self.api_todo = api_todo
