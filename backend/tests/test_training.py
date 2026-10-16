import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import init_db


class TestTraining(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Login/Register
        resp = cls.client.post("/api/auth/register", json={
            "name": "Quiz Taker",
            "email": "trainee@testing.com",
            "company": "Training Corp",
            "password": "Password123"
        })
        if resp.status_code == 201:
            cls.token = resp.get_json()["token"]
        else:
            login = cls.client.post("/api/auth/login", json={
                "email": "trainee@testing.com",
                "password": "Password123"
            })
            cls.token = login.get_json()["token"]

    def test_01_fetch_questions(self):
        resp = self.client.get(
            "/api/training/questions",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["questions"]), 5)

        # CRITICAL TEST: Verify correct answers are NOT exposed
        for q in data["questions"]:
            self.assertNotIn("correct_answer", q)
            self.assertNotIn("explanation", q)
            self.assertEqual(len(q["options"]), 4)

    def test_02_submit_quiz_answers(self):
        # Submit correct answers for questions 1 and 2
        resp = self.client.post(
            "/api/training/submit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "answers": {
                    "1": "Verify the sender and link before clicking",
                    "2": "A9!kP#72zL@4"
                }
            }
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["score"], 2)
        self.assertIn("percentage", data)
        self.assertIn("results", data)

    def test_03_training_history(self):
        resp = self.client.get(
            "/api/training/history",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertGreaterEqual(len(data["history"]), 1)


if __name__ == "__main__":
    unittest.main()
