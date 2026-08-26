import uuid

from faker import Faker

fake = Faker()


class CommentPayload:

    @staticmethod
    def create_comment_payload() -> dict:
        return {
            "name": fake.name(),
            "email": f"comment-{uuid.uuid4().hex}@example.com",
            "body": fake.paragraph(nb_sentences=2),
        }
