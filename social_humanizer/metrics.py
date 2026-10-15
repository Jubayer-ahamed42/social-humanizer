"""
Text quality, burstiness, AI-cliché evaluation, and Social Media Algorithmic Risk Auditor.
Works in pure Python with zero mandatory external dependencies.
"""

from collections import Counter
from dataclasses import dataclass, field
import math
import re
from typing import List, Tuple, Dict, Any, Optional

# Regex matching Unicode emojis across all major emoji blocks (emoticons, pictographs, dingbats, flags)
EMOJI_PATTERN = re.compile(
    r"(?:"
    r"[\U0001F300-\U0001FAFF]|"  # Emoticons, Pictographs, Symbols
    r"[\U0001F1E6-\U0001F1FF]{2}|"  # Flag pairs
    r"[\u2600-\u27BF]|"          # Misc symbols, Dingbats
    r"[\u2300-\u23FF]|"          # Misc technical
    r"[\u2B50\u2B55\u2934\u2935\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE]"
    r")(?:[\uFE00-\uFE0F]|\U0001F3FB|\U0001F3FC|\U0001F3FD|\U0001F3FE|\U0001F3FF)?",
    flags=re.UNICODE,
)


def extract_emojis(text: str) -> List[str]:
    """
    Extracts all emoji characters from text using pure Python standard library regex.
    Zero external dependencies.
    """
    return EMOJI_PATTERN.findall(text)


# Known AI clichés and buzzwords (English and Bengali)
ENGLISH_AI_CLICHES = [
    r"\bdelve\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bbeacon\b",
    r"\bgame[ -]changer\b",
    r"\brevolutionize\b",
    r"\belevate\b",
    r"\bfoster\b",
    r"\bin today's (?:fast[ -]paced|digital|interconnected|modern) (?:world|landscape|era)\b",
    r"\blandscape\b",
    r"\bseamlessly?\b",
    r"\b(?:let's|let us) dive in\b",
    r"\bunlock (?:the|your) (?:power|potential)\b",
    r"\bplethora\b",
    r"\bpivotal\b",
    r"\bharness (?:the|your)?\b",
    r"\bit's important to remember\b",
    r"\bin conclusion\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bnavigating the\b",
    r"\ba testament to\b",
    r"\brealm\b",
    r"\bembark\b",
    r"\bharnessing the power\b",
    r"\bvital role\b",
    r"\bever[ -]evolving\b",
    r"\bfast[ -]paced world\b",
    r"\bdemystify\b",
    r"\bsupercharge\b",
    r"\bcutting[ -]edge\b",
    r"\bunleash (?:the|your)\b",
    r"\bcornerstone\b",
    r"\bparadigm shift\b",
    r"\blook no further\b",
    r"\bat the end of the day\b",
    r"\bgroundbreaking\b",
    r"\bwithout further ado\b",
    r"\bit goes without saying\b",
    r"\bshed light on\b",
    r"\bholistic approach\b",
]

BENGALI_AI_CLICHES = [
    r"আজকের (?:দ্রুত পরিবর্তনশীল|ডিজিটাল|আধুনিক|প্রতিযোগিতামূলক) (?:বিশ্বে|যুগে|দুনিয়ায়|সময়ে)",
    r"আসুন জেনে (?:নিই|নেওয়া যাক|নেব|নেয়া যাক)",
    r"আসুন এক নজরে দেখে নেওয়া যাক",
    r"(?:সাফল্যের|সফলতার) (?:মূল )?চাবিকাঠি",
    r"গুরুত্ব অপরিসীম",
    r"বৈপ্লবিক (?:পদক্ষেপ|পরিবর্তন)",
    r"অবিচ্ছেদ্য অংশ",
    r"এক নতুন দিগন্ত",
    r"নিচে (?:বিস্তারিত )?আলোচনা করা হলো",
    r"চলুন জেনে (?:নিই|নেওয়া যাক|নেব|নেয়া যাক)",
    r"মনে রাখা জরুরি",
    r"বর্তমান যুগে",
    r"উল্লেখযোগ্য ভূমিকা পালন করে",
    r"সময়ের দাবি",
    r"আলোকপাত করা যাক",
    r"পরিশেষে বলা যায়",
    r"সমৃদ্ধশালী",
    r"অনস্বীকার্য",
    r"যুগান্তকারী (?:পদক্ষেপ|পরিবর্তন)",
    r"দৃষ্টি আকর্ষণ করছি",
    r"সহজে বলা যায়",
]

EMOJI_BULLET_CHARS = r"🚀🔥💡🎯✨🌟📌👉⚡💥💎✅🧵📈🧠🤖"
SPAMMY_EMOJI_PATTERN = rf"[{EMOJI_BULLET_CHARS}][\s\t]*\*{0,2}[\w\u0980-\u09FF]"
LINE_START_EMOJI_PATTERN = rf"(?m)^[\s\t]*(?:[-*•–—]|\d+[.)]|\([a-zA-Z0-9]+\))?[\s\t]*[{EMOJI_BULLET_CHARS}]"

# Matches links with http(s), www, or common domain extensions and link shorteners
COMMON_TLDS = (
    r"com|org|net|edu|gov|io|co|me|ai|app|dev|xyz|info|biz|online|site|"
    r"store|tech|cloud|pro|ly|be|to|in|tv|so|blog|link|news|gg|design|agency|social"
)
LINK_PATTERN = (
    r"(?:https?://[^\s<>\"']+|www\.[^\s<>\"']+|"
    rf"\b[a-zA-Z0-9][-a-zA-Z0-9]*\.(?:{COMMON_TLDS})(?:/[^\s<>\"']*)?(?=[/?#\s]|$|[.,!?;:)\"'](?:\s|$)))"
)
# Matches valid social hashtags containing at least one non-digit letter/symbol; rejects pure numbers like #1
HASHTAG_PATTERN = r"(?<![\w#])#([A-Za-z0-9_\u0980-\u09FF]*[A-Za-z_\u0980-\u09FF][A-Za-z0-9_\u0980-\u09FF]*)"


@dataclass
class AlgorithmWarning:
    category: str
    severity: str  # "high", "medium", "low"
    message: str
    recommendation: str


@dataclass
class HookAnalysis:
    hook_text: str
    char_length: int
    is_punchy: bool
    has_curiosity_trigger: bool
    has_first_person: bool
    has_outbound_link: bool
    has_emoji_bullet: bool
    has_cliche: bool
    hook_score: float  # 0 to 100
    rating: str  # "Elite Hook", "Strong Hook", "Average Hook", "Weak / Scroll-Bypass"
    feedback: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hook_text": self.hook_text,
            "char_length": self.char_length,
            "is_punchy": self.is_punchy,
            "has_curiosity_trigger": self.has_curiosity_trigger,
            "has_first_person": self.has_first_person,
            "has_outbound_link": self.has_outbound_link,
            "has_emoji_bullet": self.has_emoji_bullet,
            "has_cliche": self.has_cliche,
            "hook_score": round(self.hook_score, 1),
            "rating": self.rating,
            "feedback": self.feedback,
        }


@dataclass
class AlgorithmAudit:
    has_external_links: bool
    external_links: List[str]
    has_emoji_bullet_spam: bool
    emoji_bullet_count: int
    emoji_bullet_lines: List[str]
    total_emoji_count: int
    has_excessive_emojis: bool
    hashtag_count: int
    hashtags: List[str]
    has_excessive_hashtags: bool
    has_mid_text_hashtags: bool
    burstiness_cv: float
    flagged_cliches: List[str]
    risk_level: str  # "Low Risk (Algorithm Friendly)", "Moderate Risk", "High Algorithmic Penalty Risk"
    risk_score: float  # 0 to 100
    warnings: List[AlgorithmWarning]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_external_links": self.has_external_links,
            "external_links": self.external_links,
            "has_emoji_bullet_spam": self.has_emoji_bullet_spam,
            "emoji_bullet_count": self.emoji_bullet_count,
            "emoji_bullet_lines": self.emoji_bullet_lines,
            "total_emoji_count": self.total_emoji_count,
            "has_excessive_emojis": self.has_excessive_emojis,
            "hashtag_count": self.hashtag_count,
            "hashtags": self.hashtags,
            "has_excessive_hashtags": self.has_excessive_hashtags,
            "has_mid_text_hashtags": self.has_mid_text_hashtags,
            "burstiness_cv": round(self.burstiness_cv, 2),
            "flagged_cliches": self.flagged_cliches,
            "risk_level": self.risk_level,
            "risk_score": round(self.risk_score, 1),
            "warnings": [
                {
                    "category": w.category,
                    "severity": w.severity,
                    "message": w.message,
                    "recommendation": w.recommendation,
                }
                for w in self.warnings
            ],
            "recommendations": self.recommendations,
        }


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
    # Algorithmic Auditor fields
    audit: Optional[AlgorithmAudit] = None
    has_external_links: bool = False
    external_links: List[str] = field(default_factory=list)
    hashtag_count: int = 0
    hashtags: List[str] = field(default_factory=list)
    has_excessive_hashtags: bool = False
    total_emoji_count: int = 0
    has_excessive_emojis: bool = False
    has_mid_text_hashtags: bool = False
    algorithm_risk_score: float = 0.0
    algorithm_risk_level: str = "Low Risk (Algorithm Friendly)"
    algorithm_warnings: List[str] = field(default_factory=list)
    # Lightweight enhancements
    vocabulary_entropy: float = 0.0
    lexical_diversity_ttr: float = 0.0
    estimated_read_time_seconds: int = 0
    hook_analysis: Optional[HookAnalysis] = None

    def summary(self) -> str:
        status = "[HUMAN] Human-Sounding" if self.is_human_sounding else "[AI] Robotic / AI-Like"
        lines = [
            f"Overall Status: {status} (Score: {self.human_score:.1f}/100)",
            f"Algorithmic Reach Risk: {self.algorithm_risk_level} (Penalty Risk: {self.algorithm_risk_score:.0f}/100)",
            f"Total Words: {self.word_count} | Sentences: {self.sentence_count} | Est Read: ~{self.estimated_read_time_seconds}s",
            f"Burstiness (Cadence Variance): {self.burstiness_score:.2f} (Target >= 0.45)",
            f"Vocabulary Entropy: {self.vocabulary_entropy:.2f} bits | Lexical Diversity: {self.lexical_diversity_ttr:.0%}",
            f"Reading Level: {self.grade_level} (Ease: {self.reading_ease:.1f})",
            f"Emojis: {self.total_emoji_count} / 2 max | Hashtags: {self.hashtag_count} / 2 max | Outbound Links: {len(self.external_links)}",
        ]
        if self.hook_analysis and self.hook_analysis.rating != "Empty":
            lines.append(
                f"Hook Quality: {self.hook_analysis.rating} ({self.hook_analysis.hook_score:.0f}/100) - {self.hook_analysis.feedback}"
            )
        if self.flagged_cliches:
            lines.append(f"Flagged AI Clichés: {', '.join(self.flagged_cliches)}")
        if self.has_emoji_spam:
            lines.append("Flagged: Emoji bullet point spam detected at line starts.")
        if self.has_excessive_emojis:
            lines.append(f"Flagged: Excessive emojis ({self.total_emoji_count} emojis > 2). Demoted as AI clutter.")
        if self.has_external_links:
            links_preview = ", ".join(self.external_links[:3])
            lines.append(
                f"Flagged: Outbound link in post body ({links_preview}). 50%-80% reach suppression risk."
            )
        if self.has_excessive_hashtags:
            lines.append(
                f"Flagged: Excessive hashtags ({self.hashtag_count} tags > 2). Flagged as reach-farming spam."
            )
        if self.has_mid_text_hashtags:
            lines.append("Flagged: Hashtags placed inside body paragraphs instead of at the end.")
        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f" - {rec}")
        return "\n".join(lines)



def _split_sentences(text: str) -> List[str]:
    """Splits text into sentences supporting both Latin and Bengali punctuation, preserving numbers and abbreviations."""
    pattern = (
        r"(?<!\d\.)"
        r"(?<![\u09E6-\u09EF]\.)"
        r"(?<!\b[A-Za-z]\.)"
        r"(?<!\be\.g\.)"
        r"(?<!\bi\.e\.)"
        r"(?<!\betc\.)"
        r"(?<!\bvs\.)"
        r"(?<!\bDr\.)"
        r"(?<!\bMr\.)"
        r"(?<!\bMs\.)"
        r"(?<=[.!?।])\s+|\n+"
    )
    raw_sentences = re.split(pattern, text, flags=re.IGNORECASE)
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences if sentences else [text.strip()] if text.strip() else []


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
        return (sentence_lengths[0] if n == 1 else 0.0), 0.0, 0.0

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
    """Detects blacklisted AI words and robotic phrases in English and Bengali."""
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


def extract_links(text: str) -> List[str]:
    """Extracts raw URLs and web addresses from text, stripping trailing punctuation."""
    raw_matches = re.findall(LINK_PATTERN, text)
    cleaned = []
    for link in raw_matches:
        c = link.rstrip(".,!?;:)\"']")
        if c and c not in cleaned:
            cleaned.append(c)
    return cleaned


def extract_hashtags(text: str) -> List[str]:
    """Extracts all hashtags (#tag) from text."""
    matches = re.findall(HASHTAG_PATTERN, text)
    return [f"#{m}" for m in matches]


def calculate_shannon_entropy(words: List[str]) -> Tuple[float, float]:
    """
    Computes Shannon Vocabulary Entropy (bits per word) and Lexical Diversity (Type-Token Ratio, TTR).
    Pure Python math.log2 with zero external dependencies.
    - Low entropy (< 3.0 bits) indicates repetitive vocabulary typical of basic AI text.
    - High entropy (>= 3.8 bits) indicates rich, human lexical variance.
    """
    if not words:
        return 0.0, 0.0
    total_words = len(words)
    counts = Counter(w.lower() for w in words)
    unique_words = len(counts)
    ttr = (unique_words / total_words) if total_words > 0 else 0.0

    entropy = 0.0
    for count in counts.values():
        p = count / total_words
        entropy -= p * math.log2(p)

    return round(entropy, 2), round(ttr, 2)


def analyze_hook(text: str) -> HookAnalysis:
    """
    Analyzes the opening hook (the first 120-140 characters before the mobile '...see more' fold).
    Evaluates stop-scroll rate, curiosity triggers, first-person voice, and fatal algorithmic penalties.
    """
    clean_text = text.strip()
    if not clean_text:
        return HookAnalysis(
            hook_text="",
            char_length=0,
            is_punchy=False,
            has_curiosity_trigger=False,
            has_first_person=False,
            has_outbound_link=False,
            has_emoji_bullet=False,
            has_cliche=False,
            hook_score=0.0,
            rating="Empty",
            feedback="Post is empty.",
        )

    # First sentence or first line
    sentences = _split_sentences(clean_text)
    first_sentence = sentences[0] if sentences else clean_text
    first_line = clean_text.splitlines()[0] if clean_text.splitlines() else clean_text

    # The hook sample is the first line or first sentence, up to 140 chars
    hook_sample = first_line if len(first_line) <= 140 else clean_text[:140]
    hook_len = len(first_sentence)

    # Checks
    has_link = bool(extract_links(hook_sample))
    has_bullet = bool(re.search(LINE_START_EMOJI_PATTERN, hook_sample)) or bool(
        re.search(SPAMMY_EMOJI_PATTERN, hook_sample)
    )
    cliches_in_hook = detect_cliches(hook_sample)
    has_cliche = len(cliches_in_hook) > 0

    first_person_pattern = r"(?i)\b(i|my|me|we|our|myself)\b|(?:\b(?:আমি|আমার|আমরা|আমাদের)\b)"
    has_first_person = bool(re.search(first_person_pattern, hook_sample))

    curiosity_pattern = (
        r"(?:\?|why|how|never|secret|mistake|truth|actually|stop|nobody|confession|"
        r"কেন|কীভাবে|কিভাবে|ভুল|রহস্য|সত্যি|আসলে|কখনোই|বন্ধ করুন|সবচেয়ে বড়)"
    )
    has_curiosity = bool(re.search(curiosity_pattern, hook_sample, re.IGNORECASE))
    is_punchy = 15 <= hook_len <= 125

    # Scoring
    score = 50.0
    if is_punchy:
        score += 15.0
    if has_curiosity:
        score += 20.0
    if has_first_person:
        score += 15.0

    if has_link:
        score -= 40.0
    if has_bullet:
        score -= 30.0
    if has_cliche:
        score -= 30.0

    score = max(0.0, min(100.0, score))

    if score >= 80.0:
        rating = "Elite Hook"
        feedback = "Outstanding stop-scroll hook. Fits before the fold with high curiosity/story pull."
    elif score >= 60.0:
        rating = "Strong Hook"
        feedback = "Solid opening. Clear and conversational."
    elif score >= 40.0:
        rating = "Average Hook"
        feedback = "Functional opening, but could be punchier or inject a stronger curiosity gap."
    else:
        rating = "Weak / Scroll-Bypass"
        feedback = "High scroll-away risk. Avoid links/AI clichés in the first line and lead with an authentic hook."

    return HookAnalysis(
        hook_text=first_sentence[:140],
        char_length=len(first_sentence),
        is_punchy=is_punchy,
        has_curiosity_trigger=has_curiosity,
        has_first_person=has_first_person,
        has_outbound_link=has_link,
        has_emoji_bullet=has_bullet,
        has_cliche=has_cliche,
        hook_score=score,
        rating=rating,
        feedback=feedback,
    )


def audit_algorithm(
    text: str,
    burstiness_cv: Optional[float] = None,
    sentence_count: int = 1,
    avg_sentence_len: float = 0.0,
    platform: Optional[str] = None,
) -> AlgorithmAudit:
    """
    Performs comprehensive Algorithmic Risk Auditing for social platforms:
    - Outbound link detection & reach penalty warnings (50%-80% algorithmic suppression)
    - Line-initial emoji bullet point spam
    - Global emoji count audit (demotes posts with > 1-2 emojis as synthetic AI clutter)
    - Excessive hashtags (> 2 hashtags penalized per 2026 platform algorithms)
    - Mid-text hashtag placement audit (hashtags must be placed at the end)
    - Monotonous sentence cadence (low burstiness CV)
    - Enriched English and Bengali AI clichés
    - Platform-specific algorithmic constraints (Threads 500 chars, Instagram unclickable URLs, etc.)
    """
    links = extract_links(text)
    has_links = len(links) > 0

    # Line start emoji bullets
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    emoji_bullet_lines = [
        ln for ln in lines if re.search(LINE_START_EMOJI_PATTERN, ln)
    ]
    # Also verify inline spam pattern
    has_emoji_bullet_spam = bool(emoji_bullet_lines) or bool(
        re.search(SPAMMY_EMOJI_PATTERN, text)
    )
    bullet_count = len(emoji_bullet_lines) if emoji_bullet_lines else (1 if has_emoji_bullet_spam else 0)

    # Total Emojis across the text (Max 1-2 allowed)
    all_emojis = extract_emojis(text)
    total_emoji_count = len(all_emojis)
    has_excessive_emojis = total_emoji_count > 2

    # Hashtags (Max 1-2 allowed at the end)
    hashtags = extract_hashtags(text)
    hashtag_count = len(hashtags)
    has_excessive_hashtags = hashtag_count > 2

    # Mid-text hashtags check
    has_mid_text_hashtags = False
    if hashtags and len(text) > 0:
        first_tag_pos = text.find(hashtags[0])
        # If the first hashtag appears in the first 70% of the post, flag as mid-text
        if (first_tag_pos / len(text)) < 0.70:
            has_mid_text_hashtags = True

    # Clichés
    flagged = detect_cliches(text)

    # CV
    cv = burstiness_cv if burstiness_cv is not None else 0.0

    warnings: List[AlgorithmWarning] = []
    rec_texts: List[str] = []

    risk_score = 0.0

    # 1. Outbound Link Audit
    if has_links:
        risk_score += 35.0
        link_str = ", ".join(links[:2]) + ("..." if len(links) > 2 else "")
        w = AlgorithmWarning(
            category="Outbound Link Penalty",
            severity="high",
            message=(
                f"External link detected in post body ({link_str}). "
                "Major algorithms (Facebook, LinkedIn, Threads, X) penalize posts with external links "
                "by 50%-80% to keep users inside their walled garden."
            ),
            recommendation=(
                "Move the link to the first comment or bio ('Link in 1st comment 💬' or 'Link in bio') "
                "to preserve 100% of organic distribution."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 2. Emoji Bullet Spam Audit
    if has_emoji_bullet_spam:
        risk_score += 25.0
        count_str = f" ({bullet_count} line{'s' if bullet_count != 1 else ''})" if bullet_count > 0 else ""
        w = AlgorithmWarning(
            category="Emoji Bullet Spam",
            severity="medium",
            message=(
                f"Line-starting emoji bullets detected{count_str}. "
                "Modern social algorithms and readers instantly identify bulleted emojis (🚀, 🔥, 💡, 🎯, ✨) "
                "as synthetic ChatGPT formatting, leading to lower dwell time and engagement drop."
            ),
            recommendation=(
                "Remove hype emojis from bullet starts. Use natural conversational paragraphs "
                "or clean numbered lists (1, 2, 3)."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 3. Excessive Emoji Count Audit (Global Limit: Max 1-2)
    if has_excessive_emojis:
        risk_score += 20.0 if total_emoji_count <= 4 else 30.0
        w = AlgorithmWarning(
            category="Excessive Emojis",
            severity="high" if total_emoji_count > 3 else "medium",
            message=(
                f"Excessive emojis detected ({total_emoji_count} emojis > 2). "
                "2026 algorithms and readers flag posts with > 1-2 emojis as low-effort synthetic AI clutter."
            ),
            recommendation=(
                "Limit emojis to maximum 1 or 2 subtle emojis across the entire post (or zero)."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 4. Excessive Hashtags Audit (Global Limit: Max 1-2 at end)
    if has_excessive_hashtags:
        risk_score += 20.0 if hashtag_count <= 4 else 30.0
        w = AlgorithmWarning(
            category="Excessive Hashtags",
            severity="medium" if hashtag_count <= 4 else "high",
            message=(
                f"Excessive hashtags detected ({hashtag_count} tags > 2). "
                "Modern 2026 social algorithms treat hashtag stuffing as engagement-bait spam and demote distribution."
            ),
            recommendation=(
                "Keep hashtags to maximum 1-2 targeted niche tags at the very end of the post, or 0 for Twitter/Threads/Facebook."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 5. Mid-Text Hashtag Placement Audit
    if has_mid_text_hashtags:
        risk_score += 10.0
        w = AlgorithmWarning(
            category="Mid-Text Hashtags",
            severity="medium",
            message=(
                "Hashtags detected inside body paragraphs. "
                "Placing hashtags in the middle of sentences disrupts reading cadence and triggers spam heuristics."
            ),
            recommendation=(
                "Move hashtags strictly to the very bottom of the post, or remove them entirely."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 6. Cadence / Burstiness Audit
    if sentence_count >= 3 and cv < 0.35:
        risk_score += 20.0
        w = AlgorithmWarning(
            category="Cadence / Monotony",
            severity="medium",
            message=(
                f"Low burstiness variance (CV = {cv:.2f}, avg sentence length {avg_sentence_len:.1f} words). "
                "Uniform sentence length is the primary statistical marker utilized by AI classifiers."
            ),
            recommendation=(
                "Inject high rhythm variance: write punchy 2-4 word sentences immediately followed by "
                "longer conversational explanations."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 7. Cliché Blacklist Audit
    if flagged:
        cliche_risk = min(40.0, len(flagged) * 15.0)
        risk_score += cliche_risk
        w = AlgorithmWarning(
            category="AI Cliché Blacklist",
            severity="high" if len(flagged) >= 2 else "medium",
            message=(
                f"Detected {len(flagged)} blacklisted AI buzzwords/phrases: {', '.join(flagged)}."
            ),
            recommendation=(
                f"Strip or rewrite flagged clichés ({', '.join(flagged)}) with authentic, grounded personal wording."
            ),
        )
        warnings.append(w)
        rec_texts.append(w.recommendation)

    # 8. Platform-Specific Constraints
    plat = platform.lower() if platform else ""
    if plat in ("threads", "meta_threads"):
        if len(text) > 500:
            risk_score += 30.0
            w = AlgorithmWarning(
                category="Platform Constraint (Threads)",
                severity="high",
                message=f"Post length ({len(text)} chars) exceeds Threads 500-character single post limit.",
                recommendation="Shorten post under 500 characters or split into a numbered thread (1/2, 2/2).",
            )
            warnings.append(w)
            rec_texts.append(w.recommendation)
        if hashtag_count > 1:
            w = AlgorithmWarning(
                category="Platform Constraint (Threads)",
                severity="low",
                message=f"Threads only natively indexes 1 topic tag per post ({hashtag_count} tags found).",
                recommendation="Reduce to exactly 1 native topic tag for optimal Threads search indexing.",
            )
            warnings.append(w)
            rec_texts.append(w.recommendation)

    elif plat in ("instagram", "ig"):
        if has_links:
            w = AlgorithmWarning(
                category="Platform Constraint (Instagram)",
                severity="high",
                message="URLs are NOT clickable in Instagram captions and degrade readability.",
                recommendation="Replace link with 'Link in bio 🔗' or direct message trigger ('Comment INFO for link').",
            )
            warnings.append(w)
            rec_texts.append(w.recommendation)

    elif plat in ("twitter", "x"):
        if len(text) > 280 and not re.search(r"\b1/\d+\b", text):
            risk_score += 25.0
            w = AlgorithmWarning(
                category="Platform Constraint (Twitter/X)",
                severity="high",
                message=f"Text length ({len(text)} chars) exceeds the 280-character standard tweet limit.",
                recommendation="Condense under 280 characters or structure as a multi-tweet thread (1/n, 2/n).",
            )
            warnings.append(w)
            rec_texts.append(w.recommendation)

    # Normalize Risk Level
    risk_score = min(100.0, max(0.0, risk_score))
    if risk_score < 25.0:
        risk_level = "Low Risk (Algorithm Friendly)"
    elif risk_score < 60.0:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Algorithmic Penalty Risk"

    return AlgorithmAudit(
        has_external_links=has_links,
        external_links=links,
        has_emoji_bullet_spam=has_emoji_bullet_spam,
        emoji_bullet_count=bullet_count,
        emoji_bullet_lines=emoji_bullet_lines,
        total_emoji_count=total_emoji_count,
        has_excessive_emojis=has_excessive_emojis,
        hashtag_count=hashtag_count,
        hashtags=hashtags,
        has_excessive_hashtags=has_excessive_hashtags,
        has_mid_text_hashtags=has_mid_text_hashtags,
        burstiness_cv=cv,
        flagged_cliches=flagged,
        risk_level=risk_level,
        risk_score=risk_score,
        warnings=warnings,
        recommendations=rec_texts,
    )


def evaluate_text(text: str, platform: Optional[str] = None) -> MetricReport:
    """
    Full text quality analysis calculating burstiness, readability, AI presence,
    Shannon vocabulary entropy, 120-character hook quality, and comprehensive social media algorithmic risk auditing.
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

    # Shannon Vocabulary Entropy & Lexical Diversity
    entropy, ttr = calculate_shannon_entropy(words)

    # Opening Hook Analysis (first 120-140 chars before fold)
    hook = analyze_hook(text)

    # Estimated Reading Duration (seconds at 200 wpm)
    read_secs = max(1, int(round((word_count / 200.0) * 60))) if word_count > 0 else 0

    # Algorithmic Audit
    audit = audit_algorithm(
        text=text,
        burstiness_cv=cv,
        sentence_count=sentence_count,
        avg_sentence_len=avg_len,
        platform=platform,
    )

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

    # 3. Cliché penalty (deduct 15 pts per cliché, max 40)
    cliche_penalty = min(40.0, len(audit.flagged_cliches) * 15.0)

    # 4. Emoji spam penalty (deduct 15 pts)
    emoji_bullet_penalty = 15.0 if audit.has_emoji_bullet_spam else 0.0

    # 5. Global emoji count penalty (max 1-2 allowed; deduct 15 pts if > 2)
    emoji_excess_penalty = 15.0 if audit.has_excessive_emojis else 0.0

    # 6. Outbound link reach penalty (deduct 10 pts from post effectiveness)
    link_penalty = 10.0 if audit.has_external_links else 0.0

    # 7. Excessive hashtag penalty (max 1-2 allowed; deduct 15 pts if > 2)
    hashtag_penalty = 15.0 if audit.has_excessive_hashtags else 0.0

    # 8. Mid-text hashtag penalty (deduct 5 pts)
    mid_tag_penalty = 5.0 if audit.has_mid_text_hashtags else 0.0

    raw_score = (
        30.0
        + burst_points
        + read_points
        - cliche_penalty
        - emoji_bullet_penalty
        - emoji_excess_penalty
        - link_penalty
        - hashtag_penalty
        - mid_tag_penalty
    )
    human_score = max(5.0, min(100.0, raw_score))

    # Compile unified recommendations
    recommendations = list(audit.recommendations)
    if ease < 50 and "Simplify vocabulary" not in " ".join(recommendations):
        recommendations.append(
            "Simplify vocabulary and sentence structures for better readability."
        )

    # Human-sounding threshold: high human score, zero clichés, no emoji spam/excess, no link penalties, no hashtag spam
    is_human = (
        human_score >= 70.0
        and len(audit.flagged_cliches) == 0
        and not audit.has_emoji_bullet_spam
        and not audit.has_excessive_emojis
        and not audit.has_external_links
        and not audit.has_excessive_hashtags
    )

    algorithm_warning_msgs = [w.message for w in audit.warnings]

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
        flagged_cliches=audit.flagged_cliches,
        has_emoji_spam=audit.has_emoji_bullet_spam,
        is_human_sounding=is_human,
        recommendations=recommendations,
        audit=audit,
        has_external_links=audit.has_external_links,
        external_links=audit.external_links,
        hashtag_count=audit.hashtag_count,
        hashtags=audit.hashtags,
        has_excessive_hashtags=audit.has_excessive_hashtags,
        total_emoji_count=audit.total_emoji_count,
        has_excessive_emojis=audit.has_excessive_emojis,
        has_mid_text_hashtags=audit.has_mid_text_hashtags,
        algorithm_risk_score=audit.risk_score,
        algorithm_risk_level=audit.risk_level,
        algorithm_warnings=algorithm_warning_msgs,
        vocabulary_entropy=entropy,
        lexical_diversity_ttr=ttr,
        estimated_read_time_seconds=read_secs,
        hook_analysis=hook,
    )

