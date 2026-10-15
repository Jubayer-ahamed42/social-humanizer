"""
Unit tests for CLI commands and Rich terminal output rendering.
"""

import io
import sys
import unittest
from unittest.mock import patch

from social_humanizer.cli import main, render_burstiness_meter


class TestCLI(unittest.TestCase):
    def test_burstiness_meter(self):
        meter_high = render_burstiness_meter(0.55)
        self.assertIn("Dynamic Human Cadence", meter_high)

        meter_low = render_burstiness_meter(0.15)
        self.assertIn("Monotonous AI Pattern", meter_low)

    def test_cli_prompt_threads(self):
        with patch("sys.argv", ["social-humanizer", "prompt", "-p", "threads"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("SYSTEM PROMPT FOR THREADS", output)
                self.assertIn("500 characters", output)

    def test_cli_prompt_instagram(self):
        with patch("sys.argv", ["social-humanizer", "prompt", "-p", "instagram"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("SYSTEM PROMPT FOR INSTAGRAM", output)
                self.assertIn("125-Character Hook", output)

    def test_cli_score_command(self):
        sample = (
            "🚀 Elevate your productivity today! In today's fast-paced digital world, "
            "we delve into tools: https://example.com/tool #tech #ai #saas #future"
        )
        with patch("sys.argv", ["social-humanizer", "score", sample, "-p", "linkedin"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                # Should contain metrics / warnings
                self.assertTrue(len(output) > 50)

    def test_cli_score_plain_fallback(self):
        from social_humanizer.metrics import evaluate_text
        from social_humanizer.cli import print_plain_report

        report = evaluate_text("Clean simple test post.")
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            print_plain_report(report, platform="facebook")
            output = fake_out.getvalue()
            self.assertIn("Overall Status:", output)
            self.assertIn("Target Platform: FACEBOOK", output)


    def test_cli_score_piped_stdin(self):
        sample = "Here is a clean post piped through standard input for testing."
        with patch("sys.argv", ["social-humanizer", "score", "-p", "twitter"]):
            with patch("sys.stdin.isatty", return_value=False):
                with patch("sys.stdin.read", return_value=sample):
                    with patch("sys.stdout", new=io.StringIO()) as fake_out:
                        main()
                        output = fake_out.getvalue()
                        self.assertIn("Human Score", output)
                        self.assertIn("TWITTER", output)

    def test_cli_run_command(self):
        draft = "Why learning to code is like learning to play an instrument."
        with patch("sys.argv", ["social-humanizer", "run", draft, "-p", "threads"]):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn("GENERATED / STRUCTURED OUTPUT", output)
                self.assertIn("EVALUATION REPORT", output)


if __name__ == "__main__":
    unittest.main()
