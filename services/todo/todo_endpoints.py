class TodoEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_todo(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}/todos"

    def get_list_todos(self) -> str:
        return f"{self.base_url}/todos"

    def get_list_todos_by_user_id(self, user_id: int | str) -> str:
        return f"{self.base_url}/users/{user_id}/todos"

    def get_todo_by_id(self, todo_id: int | str) -> str:
        return f"{self.base_url}/todos/{todo_id}"

    def update_todo(self, todo_id: int | str) -> str:
        return f"{self.base_url}/todos/{todo_id}"

    def delete_todo(self, todo_id: int | str) -> str:
        return f"{self.base_url}/todos/{todo_id}"
