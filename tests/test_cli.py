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


    def test_cli_score_lint_failure(self):
        spam_text = "🚀 Elevate your brand in today's fast-paced digital world! https://spam.com #tag1 #tag2 #tag3 #tag4"
        with patch("sys.argv", ["social-humanizer", "score", spam_text, "--lint"]):
            with patch("sys.stdout", new=io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

    def test_cli_score_lint_success(self):
        clean_human = (
            "I noticed something strange yesterday. "
            "Computers are fundamentally dumb. "
            "If you miss a single semicolon, the entire system stops. "
            "Has anyone else spent a whole night tracking down a typo?"
        )
        with patch("sys.argv", ["social-humanizer", "score", clean_human, "--lint"]):
            with patch("sys.stdout", new=io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

    def test_cli_copy_to_clipboard(self):
        from social_humanizer.cli import copy_to_clipboard
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = mock_popen.return_value
            mock_proc.communicate.return_value = (b"", b"")
            mock_proc.returncode = 0
            res = copy_to_clipboard("Test copy text")
            self.assertTrue(res)


if __name__ == "__main__":
    unittest.main()

