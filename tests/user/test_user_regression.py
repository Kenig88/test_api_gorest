import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.regression
class TestUserRegression(BaseTest):

    @allure.title("Create user: response matches payload")
    def test_create_user(self, created_user):
        payload = UserPayloads.create_user_payload()
        user = created_user(payload)
        assert user.id > 0
        assert user.name == payload["name"]
        assert user.email == payload["email"]
        assert user.gender == payload["gender"]
        assert user.status == payload["status"]
        got = self.api_user.get_user_by_id(user.id)
        assert got == user

    @allure.title("Get users list with pagination: page={page}, per_page={per_page}")
    @pytest.mark.parametrize(
        "page, per_page",
        [
            (1, 1),
            (1, 10),
            (1, 25),
            (2, 10)]
    )
    def test_get_list_users(self, page, per_page):
        response = self.api_user.get_list_users(page=page, per_page=per_page)
        assert len(response.data) <= per_page
        assert response.page == page
        assert response.limit == per_page
        assert response.total >= 0
        assert response.pages >= 1

    @allure.title("Get created user by ID")
    def test_get_user_by_id(self, created_user):
        user = created_user()
        got = self.api_user.get_user_by_id(user.id)
        assert got == user

    @allure.title("Update user")
    def test_update_user(self, created_user):
        user = created_user()
        update_payload = UserPayloads.update_user_payload()
        updated = self.api_user.update_user(user_id=user.id, payload=update_payload)
        assert updated.id == user.id
        assert updated.name == update_payload["name"]
        assert updated.email == update_payload["email"]
        assert updated.gender == update_payload["gender"]
        assert updated.status == update_payload["status"]
        assert updated.status != user.status
        got = self.api_user.get_user_by_id(user.id)
        assert got == updated

    @allure.title("Delete user")
    def test_delete_user(self, created_user):
        user = created_user()
        deleted = self.api_user.delete_user(user.id)
        assert deleted.id == user.id
        error = self.api_user.get_user_by_id(user.id, expected_status_code=404)
        assert error.status_code == 404
