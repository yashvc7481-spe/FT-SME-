import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phishing_detector import analyze_phishing_url


class TestPhishingDetector(unittest.TestCase):
    def test_01_legitimate_url(self):
        res = analyze_phishing_url("https://www.google.com")
        self.assertEqual(res["risk_level"], "Low")
        self.assertLess(res["risk_score"], 25)
        self.assertTrue(res["normalized_url"].startswith("https://"))

    def test_02_malformed_url(self):
        res = analyze_phishing_url("invalid:url with illegal <chars>")
        self.assertEqual(res["risk_level"], "Critical")
        self.assertEqual(res["risk_score"], 100)

    def test_03_ip_address_host(self):
        res = analyze_phishing_url("http://192.168.1.1/login")
        self.assertIn(res["risk_level"], ("High", "Critical"))
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_IP_HOST", triggered)

    def test_04_excessive_subdomains(self):
        res = analyze_phishing_url("https://sub1.sub2.sub3.sub4.sub5.targetdomain.com/index.html")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_EXCESSIVE_SUBDOMAINS", triggered)

    def test_05_brand_impersonation(self):
        res = analyze_phishing_url("https://secure-login.paypal.account-verification-portal.com/auth")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_BRAND_IMPERSONATION", triggered)
        self.assertIn(res["risk_level"], ("High", "Critical"))

    def test_06_url_containing_credentials(self):
        res = analyze_phishing_url("https://victim_user:stolenpass@badactor.com/login")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_EMBEDDED_CREDS", triggered)

    def test_07_punycode_domain(self):
        res = analyze_phishing_url("https://xn--pple-43d.com/support")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_PUNYCODE_HOMOGLYPH", triggered)

    def test_08_url_shortener(self):
        res = analyze_phishing_url("https://bit.ly/3xyz789")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_URL_SHORTENER", triggered)
        # Verify shortener alone does not falsely classify as critical phishing
        self.assertNotEqual(res["risk_level"], "Critical")

    def test_09_unusually_long_url(self):
        long_url = "https://example.com/very/long/nested/path/" + ("a" * 120) + "/session?token=abc"
        res = analyze_phishing_url(long_url)
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_URL_LENGTH", triggered)

    def test_10_http_vs_https(self):
        res_http = analyze_phishing_url("http://example.com")
        res_https = analyze_phishing_url("https://example.com")
        self.assertGreater(res_http["risk_score"], res_https["risk_score"])
        # HTTP alone must not trigger high or critical phishing alert
        self.assertEqual(res_http["risk_level"], "Low")

    def test_11_suspicious_query_params(self):
        res = analyze_phishing_url("https://legit-site.com/auth?redirect=https://evil-destination.com&token=123")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_SUSPICIOUS_QUERY", triggered)

    def test_12_excessive_hyphens(self):
        res = analyze_phishing_url("https://my-secure-bank-login-portal-verification.com")
        triggered = [r["id"] for r in res["rule_results"] if r["triggered"]]
        self.assertIn("RULE_EXCESSIVE_HYPHENS", triggered)


if __name__ == "__main__":
    unittest.main()
