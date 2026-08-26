import uuid

from faker import Faker

fake = Faker()


class UserPayloads:

    @staticmethod
    def create_user_payload() -> dict:
        return {
            "name": fake.name(),
            "email": f"autotest-{uuid.uuid4().hex}@example.com",
            "gender": fake.random_element(elements=("male", "female")),
            "status": "active",
        }

    @staticmethod
    def update_user_payload() -> dict:
        return {
            "name": fake.name(),
            "email": f"autotest-{uuid.uuid4().hex}@example.com",
            "gender": fake.random_element(elements=("male", "female")),
            "status": "inactive",
        }
