import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.smoke
class TestUserSmoke(BaseTest):
    @allure.title("Smoke: CREATE -> GET -> PUT -> GET -> DELETE -> GET 404")
    def test_user_smoke(self, created_user):
        with allure.step("Create user"):
            user = created_user()
            assert user.id > 0
            assert user.name
            assert user.email

        with allure.step("Get created user"):
            got = self.api_user.get_user_by_id(user_id=user.id)
            assert got.id == user.id
            assert got.email == user.email
            assert got.name == user.name
            assert got.gender == user.gender
            assert got.status == user.status

        with allure.step("Update user with PUT"):
            update_payload = UserPayloads.update_user_payload()
            updated = self.api_user.update_user(user_id=user.id, payload=update_payload)
            assert updated.id == user.id
            assert updated.name == update_payload["name"]
            assert updated.email == update_payload["email"]
            assert updated.gender == update_payload["gender"]
            assert updated.status == update_payload["status"]

        with allure.step("Get user after update"):
            got_after_update = self.api_user.get_user_by_id(user_id=user.id)
            assert got_after_update == updated

        with allure.step("Delete user"):
            deleted = self.api_user.delete_user(user_id=user.id)
            assert deleted.id == user.id
            assert deleted.status_code == 204

        with allure.step("Check user is absent"):
            error = self.api_user.get_user_by_id(user_id=user.id, expected_status_code=404)
            assert error.status_code == 404
