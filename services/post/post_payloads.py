from faker import Faker

fake = Faker()


class PostPayloads:

    @staticmethod
    def create_post_payload() -> dict:
        return {
            "title": fake.sentence(nb_words=6),
            "body": fake.paragraph(nb_sentences=3),
        }

    @staticmethod
    def update_post_payload() -> dict:
        return {
            "title": fake.sentence(nb_words=5),
            "body": fake.paragraph(nb_sentences=2),
        }
