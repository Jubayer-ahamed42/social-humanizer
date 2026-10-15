"""
Unit tests for prompts and engine payload generation.
"""

import unittest
from social_humanizer.engine import HumanizerEngine, Platform
from social_humanizer.prompts import (
    FACEBOOK_PROMPT,
    LINKEDIN_PROMPT,
    TWITTER_PROMPT,
)


class TestPrompts(unittest.TestCase):
    def setUp(self):
        self.engine = HumanizerEngine()

    def test_prompts_contain_fabric_rules(self):
        for prompt in [FACEBOOK_PROMPT, LINKEDIN_PROMPT, TWITTER_PROMPT]:
            self.assertIn("Burstiness", prompt)
            self.assertIn("delve", prompt)
            self.assertIn("আজকের দ্রুত পরিবর্তনশীল বিশ্বে", prompt)

    def test_platform_specific_rules(self):
        self.assertIn("Facebook is a relaxed, social space", FACEBOOK_PROMPT)
        self.assertIn("LinkedIn is a professional network", LINKEDIN_PROMPT)
        self.assertIn("280 characters", TWITTER_PROMPT)

    def test_build_payload(self):
        draft = "Why learning Linux terminal is better than GUI."
        payload = self.engine.build_prompt_payload(draft, platform=Platform.FACEBOOK)
        self.assertIn("messages", payload)
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertIn(draft, payload["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()
