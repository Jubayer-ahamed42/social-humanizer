"""
Text quality, burstiness, and AI-cliché evaluation engine.
Works in pure Python with zero mandatory external dependencies.
"""

from dataclasses import dataclass, field
import math
import re
from typing import List, Tuple, Dict, Any, Optional

# Known AI clichés and buzzwords (English and Bengali)
ENGLISH_AI_CLICHES = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bbeacon\b",
    r"\bgame-changer\b",
    r"\brevolutionize\b",
    r"\belevate\b",
    r"\bfoster\b",
    r"\bin today's (?:fast-paced|digital|interconnected|modern) (?:world|landscape|era)\b",
    r"\blandscape\b",
    r"\bseamlessly?\b",
    r"\b(?:let's|let us) dive in\b",
    r"\bunlock (?:the|your) (?:power|potential)\b",
    r"\bplethora\b",
    r"\bpivotal\b",
    r"\bharness (?:the|your)\b",
    r"\bit's important to remember\b",
]

BENGALI_AI_CLICHES = [
    r"আজকের (?:দ্রুত পরিবর্তনশীল|ডিজিটাল|আধুনিক) (?:বিশ্বে|যুগে|দুনিয়ায়)",
    r"আসুন জেনে (?:নিই|নেওয়া যাক|নেব)",
    r"সাফল্যের (?:মূল )?চাবিকাঠি",
    r"গুরুত্ব অপরিসীম",
    r"বৈপ্লবিক (?:পদক্ষেপ|পরিবর্তন)",
    r"অবিচ্ছেদ্য অংশ",
    r"এক নতুন দিগন্ত",
]

SPAMMY_EMOJI_PATTERN = r"[🚀🔥💡🎯✨🌟][\s\t]*\*{0,2}[A-Za-z\u0980-\u09FF]"


@dataclass
class MetricReport:
    text: str
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    sentence_length_std_dev: float
    burstiness_score: float  # Coefficient of Variation (CV)
    human_score: float  # Normalized 0 - 100
    grade_level: str
    reading_ease: float
    flagged_cliches: List[str] = field(default_factory=list)
    has_emoji_spam: bool = False
    is_human_sounding: bool = False
    recommendations: List[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "[HUMAN] Human-Sounding" if self.is_human_sounding else "[AI] Robotic / AI-Like"
        lines = [
            f"Overall Status: {status} (Score: {self.human_score:.1f}/100)",
            f"Total Words: {self.word_count} | Sentences: {self.sentence_count}",
            f"Burstiness (Cadence Variance): {self.burstiness_score:.2f} (Higher is better)",
            f"Reading Level: {self.grade_level} (Ease: {self.reading_ease:.1f})",
        ]
        if self.flagged_cliches:
            lines.append(f"Flagged AI Clichés: {', '.join(self.flagged_cliches)}")
        if self.has_emoji_spam:
            lines.append("Flagged: Emoji bullet point spam detected.")
        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f" - {rec}")
        return "\n".join(lines)


def _split_sentences(text: str) -> List[str]:
    """Splits text into sentences supporting both Latin and Bengali punctuation."""
    # Split by '.', '!', '?', or Bengali Dari '।' followed by space or newline
    raw_sentences = re.split(r"(?<=[.!?।])\s+|\n+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()]


def _count_syllables(word: str) -> int:
    """Heuristic syllable counter for English words."""
    word = word.lower()
    if len(word) <= 3:
        return 1
    word = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", word)
    word = re.sub(r"^y", "", word)
    matches = re.findall(r"[aeiouy]{1,2}", word)
    return max(1, len(matches))


def calculate_burstiness(sentence_lengths: List[int]) -> Tuple[float, float, float]:
    """
    Computes mean, standard deviation, and Coefficient of Variation (CV).
    CV = sigma / mean.
    """
    n = len(sentence_lengths)
    if n <= 1:
        return 0.0, 0.0, 0.0

    mean = sum(sentence_lengths) / n
    variance = sum((x - mean) ** 2 for x in sentence_lengths) / (n - 1)
    std_dev = math.sqrt(variance)
    cv = (std_dev / mean) if mean > 0 else 0.0
    return mean, std_dev, cv


def calculate_readability(words: List[str], sentence_count: int) -> Tuple[float, str]:
    """
    Computes Flesch Reading Ease score and approximate Grade Level.
    """
    num_words = len(words)
    if num_words == 0 or sentence_count == 0:
        return 100.0, "Elementary"

    total_syllables = sum(_count_syllables(w) for w in words)
    # Flesch Reading Ease formula
    asl = num_words / sentence_count
    asw = total_syllables / num_words
    ease = 206.835 - (1.015 * asl) - (84.6 * asw)
    ease = max(0.0, min(100.0, ease))

    if ease >= 80:
        grade = "Casual & Conversational (Grade 5-6)"
    elif ease >= 65:
        grade = "Standard Social (Grade 7-8)"
    elif ease >= 50:
        grade = "High School (Grade 9-12)"
    else:
        grade = "Complex / Academic"

    return ease, grade


def detect_cliches(text: str) -> List[str]:
    """Detects blacklisted AI words and robotic phrases."""
    detected = []
    lower_text = text.lower()
    for pattern in ENGLISH_AI_CLICHES:
        matches = re.findall(pattern, lower_text, re.IGNORECASE)
        if matches:
            detected.extend(set(matches))
    for pattern in BENGALI_AI_CLICHES:
        matches = re.findall(pattern, text)
        if matches:
            detected.extend(set(matches))
    return sorted(list(set(detected)))


def evaluate_text(text: str) -> MetricReport:
    """
    Full text quality analysis calculating burstiness, readability, and AI presence.
    """
    sentences = _split_sentences(text)
    words = re.findall(r"\b[\w\u0980-\u09FF'-]+\b", text)

    word_count = len(words)
    sentence_count = len(sentences)

    sentence_lengths = [
        len(re.findall(r"\b[\w\u0980-\u09FF'-]+\b", s)) for s in sentences
    ]
    sentence_lengths = [l for l in sentence_lengths if l > 0]

    if not sentence_lengths:
        sentence_lengths = [word_count] if word_count > 0 else [1]

    avg_len, std_dev, cv = calculate_burstiness(sentence_lengths)
    ease, grade_level = calculate_readability(words, max(1, sentence_count))
    flagged = detect_cliches(text)
    has_emoji_spam = bool(re.search(SPAMMY_EMOJI_PATTERN, text))

    # Calculate 0-100 Human Score
    # 1. Burstiness component (up to 40 pts): target cv >= 0.45
    burst_points = min(40.0, (cv / 0.50) * 40.0) if cv > 0 else 10.0

    # 2. Reading Ease component (up to 30 pts): target ease between 60 and 85
    if 60 <= ease <= 90:
        read_points = 30.0
    elif ease > 90:
        read_points = 25.0
    else:
        read_points = max(5.0, (ease / 60.0) * 30.0)

    # 3. Cliché penalty (deduct 15 pts per cliché)
    cliche_penalty = min(40.0, len(flagged) * 15.0)

    # 4. Emoji spam penalty (deduct 15 pts)
    emoji_penalty = 15.0 if has_emoji_spam else 0.0

    raw_score = 30.0 + burst_points + read_points - cliche_penalty - emoji_penalty
    human_score = max(5.0, min(100.0, raw_score))

    recommendations = []
    if cv < 0.35 and sentence_count > 2:
        recommendations.append(
            "Increase sentence length variation (mix 2-3 word punchy lines with longer ones)."
        )
    if flagged:
        recommendations.append(
            f"Remove robotic AI terms: {', '.join(flagged)}"
        )
    if has_emoji_spam:
        recommendations.append(
            "Remove emoji bullet points (e.g. rocket, fire, lightbulb emojis at line starts); write natural sentences."
        )
    if ease < 50:
        recommendations.append(
            "Simplify vocabulary and sentence structures for social media readability."
        )

    is_human = human_score >= 70.0 and len(flagged) == 0 and not has_emoji_spam

    return MetricReport(
        text=text,
        word_count=word_count,
        sentence_count=sentence_count,
        avg_sentence_length=round(avg_len, 2),
        sentence_length_std_dev=round(std_dev, 2),
        burstiness_score=round(cv, 2),
        human_score=round(human_score, 1),
        grade_level=grade_level,
        reading_ease=round(ease, 1),
        flagged_cliches=flagged,
        has_emoji_spam=has_emoji_spam,
        is_human_sounding=is_human,
        recommendations=recommendations,
    )
