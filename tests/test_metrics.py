"""
Unit tests for metrics, algorithmic risk auditing, and text evaluation.
"""

import unittest
from social_humanizer.metrics import (
    evaluate_text,
    detect_cliches,
    calculate_burstiness,
    audit_algorithm,
    AlgorithmAudit,
)


class TestMetrics(unittest.TestCase):
    def test_detect_english_cliches(self):
        ai_text = "In today's fast-paced digital world, it is crucial to delve into this game-changer."
        flagged = detect_cliches(ai_text)
        self.assertTrue(any("delve" in f for f in flagged))
        self.assertTrue(any("game-changer" in f for f in flagged))

    def test_detect_enriched_english_cliches(self):
        text = "This cutting-edge framework will supercharge your workflow and demystify AI."
        flagged = detect_cliches(text)
        self.assertTrue(any("cutting-edge" in f for f in flagged))
        self.assertTrue(any("supercharge" in f for f in flagged))
        self.assertTrue(any("demystify" in f for f in flagged))

    def test_detect_bengali_cliches(self):
        bengali_ai_text = "আজকের ডিজিটাল বিশ্বে প্রোগ্রামিং শেখার গুরুত্ব অপরিসীম। আসুন জেনে নিই বিস্তারিত।"
        flagged = detect_cliches(bengali_ai_text)
        self.assertTrue(any("ডিজিটাল বিশ্বে" in f for f in flagged))
        self.assertTrue(any("আসুন জেনে নিই" in f for f in flagged))

    def test_detect_enriched_bengali_cliches(self):
        bengali_text = (
            "আসুন এক নজরে দেখে নেওয়া যাক আজকের দ্রুত পরিবর্তনশীল বিশ্বে "
            "সাফল্যের মূল চাবিকাঠি কি। নিচে আলোচনা করা হলো।"
        )
        flagged = detect_cliches(bengali_text)
        self.assertTrue(any("আসুন এক নজরে দেখে নেওয়া যাক" in f for f in flagged))
        self.assertTrue(any("দ্রুত পরিবর্তনশীল বিশ্বে" in f for f in flagged))
        self.assertTrue(any("সাফল্যের মূল চাবিকাঠি" in f for f in flagged))
        self.assertTrue(any("নিচে আলোচনা করা হলো" in f for f in flagged))

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
        self.assertFalse(report.has_external_links)
        self.assertFalse(report.has_excessive_hashtags)
        self.assertEqual(report.algorithm_risk_level, "Low Risk (Algorithm Friendly)")

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
        self.assertGreater(report.algorithm_risk_score, 30.0)

    def test_outbound_links_audit(self):
        text_with_link = (
            "Check out our new open-source release here: https://github.com/hizibizi/social-humanizer. "
            "It is completely free to use."
        )
        report = evaluate_text(text_with_link)
        self.assertTrue(report.has_external_links)
        self.assertIn("https://github.com/hizibizi/social-humanizer", report.external_links)
        self.assertGreater(report.algorithm_risk_score, 20.0)
        # Check recommendation to move link to first comment
        self.assertTrue(any("first comment" in rec for rec in report.recommendations))

    def test_emoji_bullet_spam_audit(self):
        bullet_text = (
            "Here are the top lessons:\n"
            "🚀 Build in public\n"
            "🔥 Ship fast\n"
            "💡 Listen to users\n"
            "🎯 Stay focused"
        )
        report = evaluate_text(bullet_text)
        self.assertTrue(report.has_emoji_spam)
        self.assertTrue(report.audit.has_emoji_bullet_spam)
        self.assertGreaterEqual(report.audit.emoji_bullet_count, 4)
        self.assertTrue(any("emoji" in rec.lower() for rec in report.recommendations))

    def test_excessive_hashtags_audit(self):
        hashtag_text = (
            "Loving the new social humanizer library! "
            "#ai #python #machinelearning #coding #tech #innovation"
        )
        report = evaluate_text(hashtag_text)
        self.assertEqual(report.hashtag_count, 6)
        self.assertTrue(report.has_excessive_hashtags)
        self.assertTrue(any("hashtags" in rec.lower() for rec in report.recommendations))

    def test_platform_specific_audit_threads(self):
        long_threads_post = "A" * 550
        audit = audit_algorithm(long_threads_post, platform="threads")
        self.assertTrue(any("500-character" in w.message for w in audit.warnings))

    def test_platform_specific_audit_instagram(self):
        ig_post_with_link = "New blog post out at https://myblog.com/ai-post check it out!"
        audit = audit_algorithm(ig_post_with_link, platform="instagram")
        self.assertTrue(any("not clickable" in w.message.lower() for w in audit.warnings))

    def test_audit_to_dict(self):
        report = evaluate_text("Simple clean post for testing.")
        d = report.audit.to_dict()
        self.assertIn("has_external_links", d)
        self.assertIn("burstiness_cv", d)
        self.assertIn("risk_score", d)
        self.assertIn("warnings", d)

    def test_edge_cases(self):
        # Empty text
        empty_report = evaluate_text("")
        self.assertEqual(empty_report.word_count, 0)
        self.assertEqual(empty_report.sentence_count, 0)

        # Single word
        word_report = evaluate_text("Greetings")
        self.assertEqual(word_report.word_count, 1)

        # Bengali text with dari
        bengali_text = "আমি গতকাল একটি বই পড়েছি। বইটি বেশ চমৎকার ছিল। আপনার পছন্দের বই কোনটি?"
        b_report = evaluate_text(bengali_text)
        self.assertEqual(b_report.sentence_count, 3)
        self.assertGreater(b_report.burstiness_score, 0.0)


    def test_numeric_hashtag_not_flagged(self):
        text_with_numbers = "We rank #1 in support, #2 in speed, and #3 in quality. Real tags: #growth #innovation"
        report = evaluate_text(text_with_numbers)
        self.assertEqual(report.hashtag_count, 2)
        self.assertEqual(report.hashtags, ["#growth", "#innovation"])
        self.assertFalse(report.has_excessive_hashtags)

    def test_link_shorteners_detected(self):
        text_with_shorteners = "Check our latest release on bit.ly/social-hub and lnkd.in/demo. Also ai-driven tools."
        report = evaluate_text(text_with_shorteners)
        self.assertTrue(report.has_external_links)
        self.assertTrue(any("bit.ly" in link for link in report.external_links))
        self.assertTrue(any("lnkd.in" in link for link in report.external_links))
        # Ensure hyphenated "ai-driven" is not extracted as a link
        self.assertFalse(any("ai-driven" in link for link in report.external_links))

    def test_sentence_splitting_numbers_and_abbreviations(self):
        from social_humanizer.metrics import _split_sentences
        text = "1. First point. 2. Second point. Dr. Smith agreed with i.e. the premise."
        sentences = _split_sentences(text)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "1. First point.")
        self.assertEqual(sentences[1], "2. Second point.")
        self.assertEqual(sentences[2], "Dr. Smith agreed with i.e. the premise.")

    def test_emoji_bullet_spam_markdown(self):
        markdown_bullets = (
            "Here is the plan:\n"
            "- 🚀 Build in public\n"
            "* 🔥 Ship fast\n"
            "• 💡 Listen to users"
        )
        report = evaluate_text(markdown_bullets)
        self.assertTrue(report.has_emoji_spam)
        self.assertGreaterEqual(report.audit.emoji_bullet_count, 3)
        self.assertTrue(any("3 lines" in w.message for w in report.audit.warnings if w.category == "Emoji Bullet Spam"))

    def test_unhyphenated_and_enriched_cliches(self):
        text = "This is a game changer and cutting edge technology. নিচে বিস্তারিত আলোচনা করা হলো এবং সফলতার মূল চাবিকাঠি।"
        flagged = detect_cliches(text)
        self.assertTrue(any("game changer" in f or "game-changer" in f for f in flagged))
        self.assertTrue(any("cutting edge" in f or "cutting-edge" in f for f in flagged))
        self.assertTrue(any("সফলতার" in f or "সাফল্যের" in f for f in flagged))
        self.assertTrue(any("নিচে" in f for f in flagged))


    def test_global_emoji_count_and_excess_penalty(self):
        from social_humanizer.metrics import extract_emojis
        # Post with 1-2 subtle emojis (allowed)
        clean_post = "I tried a new approach to deep work today. It made a noticeable difference. 💡"
        emojis = extract_emojis(clean_post)
        self.assertEqual(len(emojis), 1)
        clean_rep = evaluate_text(clean_post)
        self.assertEqual(clean_rep.total_emoji_count, 1)
        self.assertFalse(clean_rep.has_excessive_emojis)

        # Post with 4 scattered emojis (exceeds max 1-2 rule)
        cluttered_post = "I love coding 🚀 and learning AI 🧠 because it helps us win 🏆 every single day ✨!"
        cluttered_emojis = extract_emojis(cluttered_post)
        self.assertEqual(len(cluttered_emojis), 4)
        cluttered_rep = evaluate_text(cluttered_post)
        self.assertEqual(cluttered_rep.total_emoji_count, 4)
        self.assertTrue(cluttered_rep.has_excessive_emojis)
        self.assertTrue(any("Excessive Emojis" in w.category for w in cluttered_rep.audit.warnings))

    def test_strict_hashtag_limit_max_2(self):
        # 2 hashtags (allowed limit)
        valid_post = "Building something new in public.\n\n#buildinpublic #dev"
        rep_valid = evaluate_text(valid_post)
        self.assertEqual(rep_valid.hashtag_count, 2)
        self.assertFalse(rep_valid.has_excessive_hashtags)

        # 3 hashtags (exceeds max 2 rule)
        spam_post = "Building something new in public.\n\n#buildinpublic #dev #coding"
        rep_spam = evaluate_text(spam_post)
        self.assertEqual(rep_spam.hashtag_count, 3)
        self.assertTrue(rep_spam.has_excessive_hashtags)
        self.assertTrue(any("Excessive Hashtags" in w.category for w in rep_spam.audit.warnings))

    def test_mid_text_hashtags_flagged(self):
        # Hashtags embedded inside sentence rather than at end
        mid_tag_post = "Today we explore #deeplearning methods to understand how models learn from data. It was fascinating."
        rep = evaluate_text(mid_tag_post)
        self.assertTrue(rep.has_mid_text_hashtags)
        self.assertTrue(any("Mid-Text Hashtags" in w.category for w in rep.audit.warnings))

    def test_shannon_entropy_calculation(self):
        from social_humanizer.metrics import calculate_shannon_entropy
        # Repetitive words (low entropy)
        repetitive = ["ai", "ai", "ai", "smart", "smart", "ai"]
        entropy_low, ttr_low = calculate_shannon_entropy(repetitive)
        self.assertLess(entropy_low, 2.0)

        # Diverse words (high entropy)
        diverse = ["building", "thoughtful", "software", "requires", "deep", "focus", "and", "patience"]
        entropy_high, ttr_high = calculate_shannon_entropy(diverse)
        self.assertGreater(entropy_high, 2.5)
        self.assertEqual(ttr_high, 1.0)

    def test_hook_analysis_quality(self):
        from social_humanizer.metrics import analyze_hook
        # Strong curiosity & first-person hook
        strong_text = "I made a critical mistake with our database yesterday that cost us 4 hours. Here is what happened."
        hook = analyze_hook(strong_text)
        self.assertGreaterEqual(hook.hook_score, 70.0)
        self.assertIn(hook.rating, ["Elite Hook", "Strong Hook"])
        self.assertTrue(hook.has_first_person)
        self.assertTrue(hook.has_curiosity_trigger)

        # Bad hook with outbound link and cliché
        bad_text = "In today's fast-paced world, check out https://example.com/blog for details."
        bad_hook = analyze_hook(bad_text)
        self.assertLess(bad_hook.hook_score, 40.0)
        self.assertEqual(bad_hook.rating, "Weak / Scroll-Bypass")
        self.assertTrue(bad_hook.has_outbound_link)
        self.assertTrue(bad_hook.has_cliche)


if __name__ == "__main__":
    unittest.main()

