import unittest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import init_db


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_register_success(self):
        resp = self.client.post("/api/auth/register", json={
            "name": "Security Officer",
            "email": "officer@testenterprise.com",
            "company": "Secure Co",
            "password": "Password123"
        })
        self.assertIn(resp.status_code, (201, 409))
        if resp.status_code == 201:
            data = resp.get_json()
            self.assertTrue(data["success"])
            self.assertIn("token", data)
            self.assertEqual(data["user"]["email"], "officer@testenterprise.com")

    def test_02_register_duplicate_email(self):
        resp = self.client.post("/api/auth/register", json={
            "name": "Security Officer 2",
            "email": "officer@testenterprise.com",
            "company": "Another Co",
            "password": "Password123"
        })
        self.assertEqual(resp.status_code, 409)
        self.assertFalse(resp.get_json()["success"])

    def test_03_register_missing_fields(self):
        resp = self.client.post("/api/auth/register", json={
            "name": "Incomplete",
            "email": ""
        })
        self.assertEqual(resp.status_code, 400)

    def test_04_register_weak_password(self):
        resp = self.client.post("/api/auth/register", json={
            "name": "User",
            "email": "weak@example.com",
            "password": "short"
        })
        self.assertEqual(resp.status_code, 400)

    def test_05_login_success(self):
        resp = self.client.post("/api/auth/login", json={
            "email": "officer@testenterprise.com",
            "password": "Password123"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("token", data)

    def test_06_login_invalid_password(self):
        resp = self.client.post("/api/auth/login", json={
            "email": "officer@testenterprise.com",
            "password": "WrongPassword999"
        })
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(resp.get_json()["success"])

    def test_07_unauthorized_protected_endpoint(self):
        resp = self.client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 401)

    def test_08_invalid_token(self):
        resp = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
