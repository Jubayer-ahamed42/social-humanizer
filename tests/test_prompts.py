"""
Unit tests for prompts and engine payload generation.
"""

import unittest
from unittest.mock import patch
from social_humanizer.engine import HumanizerEngine, Platform
from social_humanizer.prompts import (
    FACEBOOK_PROMPT,
    LINKEDIN_PROMPT,
    TWITTER_PROMPT,
    THREADS_PROMPT,
    INSTAGRAM_PROMPT,
)


class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.engine = HumanizerEngine()

    def test_prompts_contain_fabric_rules(self):
        for prompt in [
            FACEBOOK_PROMPT,
            LINKEDIN_PROMPT,
            TWITTER_PROMPT,
            THREADS_PROMPT,
            INSTAGRAM_PROMPT,
        ]:
            self.assertIn("Burstiness", prompt)
            self.assertIn("delve", prompt)
            self.assertIn("আজকের দ্রুত পরিবর্তনশীল বিশ্বে", prompt)

    def test_platform_specific_rules(self):
        self.assertIn("Facebook is a relaxed, social space", FACEBOOK_PROMPT)
        self.assertIn("LinkedIn is a professional network", LINKEDIN_PROMPT)
        self.assertIn("280 characters", TWITTER_PROMPT)
        self.assertIn("500 characters", THREADS_PROMPT)
        self.assertIn("Threads is conversational", THREADS_PROMPT)
        self.assertIn("125-Character Hook", INSTAGRAM_PROMPT)
        self.assertIn("Instagram captions serve as the voice", INSTAGRAM_PROMPT)

    def test_build_payload(self):
        draft = "Why learning Linux terminal is better than GUI."
        for plat in [Platform.FACEBOOK, Platform.LINKEDIN, Platform.TWITTER, Platform.THREADS, Platform.INSTAGRAM]:
            payload = self.engine.build_prompt_payload(draft, platform=plat)
            self.assertIn("messages", payload)
            self.assertEqual(len(payload["messages"]), 2)
            self.assertEqual(payload["messages"][0]["role"], "system")
            self.assertIn(draft, payload["messages"][1]["content"])


    @patch("requests.post", side_effect=Exception("Offline fallback"))
    def test_engine_generate_all_platforms(self, mock_post):
        draft = "Here is a draft discussing open source development and tools: https://example.com/tool #ai"
        for plat in [Platform.FACEBOOK, Platform.LINKEDIN, Platform.TWITTER, Platform.THREADS, Platform.INSTAGRAM]:
            output, report = self.engine.generate(draft, platform=plat)
            self.assertTrue(len(output) > 0)
            self.assertIsNotNone(report)
            self.assertGreaterEqual(report.human_score, 60.0)
            # Ensure output is evaluated for the specific platform
            if plat == Platform.THREADS:
                self.assertLessEqual(len(output), 500)
            elif plat == Platform.TWITTER:
                self.assertFalse(report.has_external_links)

    @patch("requests.post")
    def test_engine_generate_online(self, mock_post):
        from unittest.mock import MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "This is a clean humanized thought about code."}}]
        }
        mock_post.return_value = mock_resp

        output, report = self.engine.generate("test draft", platform=Platform.LINKEDIN)
        self.assertEqual(output, "This is a clean humanized thought about code.")
        self.assertIsNotNone(report)
        self.assertEqual(report.algorithm_risk_level, "Low Risk (Algorithm Friendly)")

    def test_rewrite_offline_threads_and_instagram(self):
        robotic = "🚀 Elevate your workflow today! In today's fast-paced digital world, check our tool: https://example.com/tool #tech"
        threads_post = self.engine.rewrite_offline(robotic, platform=Platform.THREADS)
        self.assertNotIn("https://example.com/tool", threads_post.split("(Full link")[0])
        self.assertLessEqual(len(threads_post), 500)

        ig_post = self.engine.rewrite_offline(robotic, platform=Platform.INSTAGRAM)
        self.assertIn("Save this", ig_post)
        self.assertIn("Link in bio", ig_post)


if __name__ == "__main__":
    unittest.main()
