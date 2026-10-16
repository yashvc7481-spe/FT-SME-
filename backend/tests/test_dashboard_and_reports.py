import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from database import init_db


class TestDashboardAndReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Register User A
        resp_a = cls.client.post("/api/auth/register", json={
            "name": "User Alpha",
            "email": "alpha@enterprise.com",
            "company": "Alpha Corp",
            "password": "Password123"
        })
        if resp_a.status_code == 201:
            cls.token_a = resp_a.get_json()["token"]
        else:
            login_a = cls.client.post("/api/auth/login", json={
                "email": "alpha@enterprise.com",
                "password": "Password123"
            })
            cls.token_a = login_a.get_json()["token"]

        # Register User B (for tenant isolation test)
        resp_b = cls.client.post("/api/auth/register", json={
            "name": "User Beta",
            "email": "beta@isolated.com",
            "company": "Beta LLC",
            "password": "Password123"
        })
        if resp_b.status_code == 201:
            cls.token_b = resp_b.get_json()["token"]
        else:
            login_b = cls.client.post("/api/auth/login", json={
                "email": "beta@isolated.com",
                "password": "Password123"
            })
            cls.token_b = login_b.get_json()["token"]

    def test_01_dashboard_summary(self):
        resp = self.client.get(
            "/api/dashboard/summary",
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("stats", data)
        self.assertIn("health_score", data["stats"])
        self.assertEqual(data["user"]["email"], "alpha@enterprise.com")

    def test_02_tenant_isolation(self):
        # User A triggers a phishing scan
        self.client.post(
            "/api/phishing/check",
            headers={"Authorization": f"Bearer {self.token_a}"},
            json={"url": "http://10.0.0.1/admin-login"}
        )

        # Check User A's history has at least 1 scan
        hist_a = self.client.get(
            "/api/phishing/history",
            headers={"Authorization": f"Bearer {self.token_a}"}
        ).get_json()
        self.assertGreaterEqual(hist_a["total"], 1)

        # User B's history must NOT contain User A's scans
        hist_b = self.client.get(
            "/api/phishing/history",
            headers={"Authorization": f"Bearer {self.token_b}"}
        ).get_json()
        # Verify no items in B's history belong to A
        for item in hist_b["history"]:
            self.assertNotEqual(item["url"], "http://10.0.0.1/admin-login")

    def test_03_recommendations(self):
        resp = self.client.get(
            "/api/recommendations",
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(len(data["recommendations"]), 0)
        for rec in data["recommendations"]:
            self.assertIn("issue", rec)
            self.assertIn("why_it_matters", rec)
            self.assertIn("recommended_action", rec)

    def test_04_alerts_and_mark_read(self):
        # Fetch alerts for User A
        alerts_resp = self.client.get(
            "/api/alerts",
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(alerts_resp.status_code, 200)
        alerts_data = alerts_resp.get_json()

        if alerts_data["alerts"]:
            alert_id = alerts_data["alerts"][0]["id"]
            # User B attempting to mark User A's alert as read should be rejected (404/denied)
            hack_attempt = self.client.put(
                f"/api/alerts/{alert_id}/read",
                headers={"Authorization": f"Bearer {self.token_b}"}
            )
            self.assertEqual(hack_attempt.status_code, 404)

            # User A marking own alert as read should succeed
            read_resp = self.client.put(
                f"/api/alerts/{alert_id}/read",
                headers={"Authorization": f"Bearer {self.token_a}"}
            )
            self.assertEqual(read_resp.status_code, 200)

    def test_05_reports_summary(self):
        resp = self.client.get(
            "/api/reports/summary",
            headers={"Authorization": f"Bearer {self.token_a}"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("overall_health", data)
        self.assertIn("breakdown", data)


if __name__ == "__main__":
    unittest.main()
