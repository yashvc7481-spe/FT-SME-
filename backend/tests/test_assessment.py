import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import init_db


class TestAssessment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Register and get auth token
        resp = cls.client.post("/api/auth/register", json={
            "name": "Audit User",
            "email": "auditor@testing.com",
            "company": "Audit Corp",
            "password": "Password123"
        })
        if resp.status_code == 201:
            cls.token = resp.get_json()["token"]
        else:
            login = cls.client.post("/api/auth/login", json={
                "email": "auditor@testing.com",
                "password": "Password123"
            })
            cls.token = login.get_json()["token"]

    def test_01_fetch_questions(self):
        resp = self.client.get(
            "/api/assessment/questions",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["questions"]), 10)

    def test_02_submit_strong_assessment(self):
        # All yes -> score 100%, Low risk
        answers = {f"q{i}": "Yes" for i in range(1, 11)}
        resp = self.client.post(
            "/api/assessment/submit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"answers": answers}
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["score"], 100)
        self.assertEqual(data["risk_level"], "Low")

    def test_03_submit_weak_assessment(self):
        # All no -> score 0%, High risk
        answers = {f"q{i}": "No" for i in range(1, 11)}
        resp = self.client.post(
            "/api/assessment/submit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"answers": answers}
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertEqual(data["score"], 0)
        self.assertEqual(data["risk_level"], "High")
        self.assertGreater(len(data["recommendations"]), 0)

    def test_04_history_retrieval(self):
        resp = self.client.get(
            "/api/assessment/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data["history"]), 2)


if __name__ == "__main__":
    unittest.main()
