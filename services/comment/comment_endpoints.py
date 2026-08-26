class CommentEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_comment(self, post_id: int | str) -> str:
        return f"{self.base_url}/posts/{post_id}/comments"

    def get_list_comments(self):
        return f"{self.base_url}/comments"

    def get_list_comments_by_post_id(self, post_id: int | str) -> str:
        return f"{self.base_url}/posts/{post_id}/comments"

    def delete_comment(self, comment_id: int | str) -> str:
        return f"{self.base_url}/comments/{comment_id}"
