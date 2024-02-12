import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import ErrorDetail


class TestSignUpView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "strong_password",
        }
        self.short_password = {
            "username": "user",
            "email": "test@email.com",
            "password": "weak",  # Password too short
        }

    def test_sign_up_success(self):
        response = self.client.post("/auth/signup/", self.valid_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert response.data["message"] == "User Created Successfully"

        # Check user creation and token generation
        user = User.objects.get(username=self.valid_data["username"])
        assert user.email == self.valid_data["email"]

        # Clean up: delete the created user
        user.delete()

    def test_sign_up_password_too_short(self):
        response = self.client.post("/auth/signup/", self.short_password, format="json")
        error = ErrorDetail(
            string="Ensure this field has at least 8 characters.", code="min_length"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert error in response.data["password"]

        # Check that no user was created
        assert not User.objects.filter(
            username=self.short_password["username"]
        ).exists()

    def test_sign_up_duplicate_email(self):
        # Create a user with the same email beforehand
        User.objects.create_user(
            username="user1", email=self.valid_data["email"], password="password1"
        )
        error = ErrorDetail(string="Email has already been used", code="invalid")

        response = self.client.post("/auth/signup/", self.valid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in response.data
        assert error in response.data["errors"]

        # Clean up: delete the created user
        User.objects.get(username="user1").delete()


class TestLogInView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="strong_password"
        )

    def test_log_in_success(self):
        data = {"username": "test_user", "password": "strong_password"}
        response = self.client.post("/auth/login/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            "message" in response.data
            and response.data["message"] == "Login Successfull"
        )
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]

        # Verify token validity (optional)
        access_token = response.data["tokens"]["access"]
        refresh_token = response.data["tokens"]["refresh"]

    def test_log_in_invalid_credentials(self):
        data = {"username": "wrong_user", "password": "incorrect_password"}
        response = self.client.post("/auth/login/", data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert (
            "message" in response.data
            and response.data["message"] == "Invalid username or password"
        )
