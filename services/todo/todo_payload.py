from datetime import UTC, datetime, timedelta

from faker import Faker

fake = Faker()


class TodoPayloads:

    @staticmethod
    def create_todo_payload() -> dict:
        due_on = datetime.now(UTC).replace(microsecond=0) + timedelta(days=7)
        return {
            "title": fake.sentence(nb_words=6),
            "due_on": due_on.isoformat(),
            "status": "pending",
        }

    @staticmethod
    def update_todo_payload() -> dict:
        due_on = datetime.now(UTC).replace(microsecond=0) + timedelta(days=14)
        return {
            "title": fake.sentence(nb_words=5),
            "due_on": due_on.isoformat(),
            "status": "completed",
        }
