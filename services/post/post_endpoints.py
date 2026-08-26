class PostEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_post(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}/posts"

    def get_list_posts(self) -> str:
        return f"{self.base_url}/posts"

    def get_list_posts_by_user_id(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}/posts"

    def get_post_by_id(self, post_id: int | str) -> str:
        return f"{self.base_url}/posts/{post_id}"

    def update_post(self, post_id: int | str) -> str:
        return f"{self.base_url}/posts/{post_id}"

    def delete_post(self, post_id: int | str) -> str:
        return f"{self.base_url}/posts/{post_id}"
