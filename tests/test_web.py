"""
Unit tests for the standalone Web Playground server and API endpoints.
"""

import json
import threading
import unittest
import urllib.request
from http.server import HTTPServer
from examples.app import PlaygroundHandler


class TestWebPlayground(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Bind to port 0 for automatic available port selection
        cls.server = HTTPServer(("127.0.0.1", 0), PlaygroundHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_get_root(self):
        req = urllib.request.Request(f"{self.base_url}/")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read().decode("utf-8")
            self.assertIn("Social-Humanizer Playground", content)
            self.assertIn("Anti-AI Algorithm Risk Auditor", content)

    def test_api_evaluate(self):
        payload = {
            "text": "🚀 In today's fast-paced digital world, it is crucial to delve into AI. Read more: https://example.com/ai #tech #ai #dev #innovation",
            "platform": "threads",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/evaluate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertIn("human_score", res)
            self.assertIn("algorithm_risk_score", res)
            self.assertTrue(res["has_external_links"])
            self.assertTrue(res["has_emoji_spam"])
            self.assertIn("delve", res["flagged_cliches"])
            self.assertIn("audit", res)
            self.assertGreater(len(res["audit"]["warnings"]), 0)

    def test_api_prompt(self):
        payload = {"platform": "instagram"}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["platform"], "instagram")
            self.assertIn("125-Character Hook", res["prompt"])


    def test_api_generate(self):
        payload = {
            "draft": "🚀 Elevate your career! In today's fast-paced digital world, check our tool: https://example.com/tool #ai #tech #startups",
            "platform": "threads",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertIn("output", res)
            self.assertIn("human_score", res)
            self.assertIn("report", res)
            self.assertLessEqual(len(res["output"]), 500)


if __name__ == "__main__":
    unittest.main()
