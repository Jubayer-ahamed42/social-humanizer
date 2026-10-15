"""
Unit tests for metrics and text evaluation.
"""

import unittest
from social_humanizer.metrics import (
    evaluate_text,
    detect_cliches,
    calculate_burstiness,
)


class TestMetrics(unittest.TestCase):
    def test_detect_english_cliches(self):
        ai_text = "In today's fast-paced digital world, it is crucial to delve into this game-changer."
        flagged = detect_cliches(ai_text)
        self.assertTrue(any("delve" in f for f in flagged))
        self.assertTrue(any("game-changer" in f for f in flagged))

    def test_detect_bengali_cliches(self):
        bengali_ai_text = "আজকের ডিজিটাল বিশ্বে প্রোগ্রামিং শেখার গুরুত্ব অপরিসীম। আসুন জেনে নিই বিস্তারিত।"
        flagged = detect_cliches(bengali_ai_text)
        self.assertTrue(any("ডিজিটাল বিশ্বে" in f for f in flagged))
        self.assertTrue(any("আসুন জেনে নিই" in f for f in flagged))

    def test_burstiness_variance(self):
        # Monotonous sentences (similar length)
        monotonous = [15, 16, 15, 14, 15, 16]
        _, _, cv_mono = calculate_burstiness(monotonous)

        # Varied sentences (very short and long)
        varied = [3, 24, 4, 30, 2, 18]
        _, _, cv_varied = calculate_burstiness(varied)

        self.assertGreater(cv_varied, cv_mono)

    def test_human_sounding_evaluation(self):
        # Good humanized text (casual, conversational, varied rhythm)
        human_text = (
            "I noticed something strange yesterday. "
            "Computers are fundamentally dumb. "
            "If you forget a single semicolon, the compiler completely gives up and complains. "
            "Honestly, who else has spent an entire night debugging only to find a typo?"
        )
        report = evaluate_text(human_text)
        self.assertGreaterEqual(report.human_score, 70.0)
        self.assertEqual(len(report.flagged_cliches), 0)
        self.assertFalse(report.has_emoji_spam)

    def test_robotic_evaluation(self):
        robotic_text = (
            "🚀 Elevate your productivity today! "
            "In today's fast-paced landscape, we delve into transformative solutions. "
            "🔥 Unlock your maximum potential with our game-changer toolkit."
        )
        report = evaluate_text(robotic_text)
        self.assertLess(report.human_score, 60.0)
        self.assertGreater(len(report.flagged_cliches), 0)
        self.assertTrue(report.has_emoji_spam)


if __name__ == "__main__":
    unittest.main()
