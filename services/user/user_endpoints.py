class UserEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_user(self) -> str:
        return f"{self.base_url}/users"

    def get_list_users(self) -> str:
        return f"{self.base_url}/users"

    def get_user_by_id(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}"

    def update_user(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}"

    def delete_user(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}"
