"""
Core Humanizer Engine coordinating prompt generation, optional LLM generation,
and deterministic metric scoring.
"""

from enum import Enum
import json
import os
from typing import Dict, Any, Optional, Tuple
import re

from .metrics import evaluate_text, extract_links, extract_hashtags, MetricReport
from .prompts.facebook import FACEBOOK_PROMPT
from .prompts.linkedin import LINKEDIN_PROMPT
from .prompts.twitter import TWITTER_PROMPT
from .prompts.threads import THREADS_PROMPT
from .prompts.instagram import INSTAGRAM_PROMPT


class Platform(str, Enum):
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    THREADS = "threads"
    INSTAGRAM = "instagram"


class HumanizerEngine:
    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initializes the Humanizer engine.
        Defaults to environment variables if not passed:
        - OPENAI_API_BASE / LOCAL_LLM_URL (default: http://localhost:11434/v1 for Ollama)
        - OPENAI_API_KEY / GEMINI_API_KEY
        - MODEL_NAME (default: llama3 / gpt-4o-mini / gemini-1.5-flash)
        """
        self.api_base = api_base or os.getenv(
            "OPENAI_API_BASE", "http://localhost:11434/v1"
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "dummy-key")
        self.model = model or os.getenv("MODEL_NAME", "llama3")

    def get_system_prompt(self, platform: Platform) -> str:
        """Returns the targeted system prompt for a social platform."""
        # Normalize to string/enum for flexible input
        plat_val = platform.value if isinstance(platform, Platform) else str(platform).lower()
        if plat_val == Platform.FACEBOOK.value:
            return FACEBOOK_PROMPT
        elif plat_val == Platform.LINKEDIN.value:
            return LINKEDIN_PROMPT
        elif plat_val == Platform.TWITTER.value:
            return TWITTER_PROMPT
        elif plat_val == Platform.THREADS.value:
            return THREADS_PROMPT
        elif plat_val == Platform.INSTAGRAM.value:
            return INSTAGRAM_PROMPT
        return FACEBOOK_PROMPT

    def build_prompt_payload(
        self, draft: str, platform: Platform = Platform.FACEBOOK
    ) -> Dict[str, Any]:
        """
        Builds a standard OpenAI-compatible chat payload ready for any LLM API
        (Gemini, OpenAI, Claude, Groq, Ollama, vLLM).
        """
        system_prompt = self.get_system_prompt(platform)
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Here is the raw topic/draft to rewrite:\n\n{draft}",
                },
            ],
            "temperature": 0.7,
        }

    def rewrite_offline(
        self, draft: str, platform: Platform = Platform.FACEBOOK
    ) -> str:
        """
        Pure-Python rule-based anti-AI transformation pipeline:
        - Strips and relocates outbound links to prevent 50%-80% algorithmic reach penalties
        - Cleans robotic emoji bullets (🚀, 🔥, 💡) into natural conversational text
        - Replaces blacklisted AI clichés (English & Bengali) with authentic human equivalents
        - Injects platform-specific hooks, cadence variance, character limits, and engagement CTAs
        """
        text = draft.strip()
        if not text:
            return ""

        plat_val = platform.value if isinstance(platform, Platform) else str(platform).lower()

        # 1. Extract and relocate outbound links
        links = extract_links(text)
        for link in links:
            text = text.replace(link, "").strip()

        # Clean multiple spaces left by link removal
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 2. Clean line-starting emoji bullet points
        clean_lines = []
        bullet_idx = 1
        for line in text.splitlines():
            line_str = line.strip()
            if re.search(r"^(?:[-*•–—]|\d+[.)])?[\s\t]*[🚀🔥💡🎯✨🌟📌👉⚡💥💎✅🧵📈🧠🤖]\s*", line_str):
                subbed = re.sub(r"^(?:[-*•–—]|\d+[.)])?[\s\t]*[🚀🔥💡🎯✨🌟📌👉⚡💥💎✅🧵📈🧠🤖]\s*", "", line_str)
                if subbed:
                    clean_lines.append(f"{bullet_idx}. {subbed}")
                    bullet_idx += 1
            else:
                clean_lines.append(line)
        text = "\n".join(clean_lines)

        # 3. Cliché replacement mappings (English and Bengali)
        cliche_replacements = [
            (r"\bin today's (?:fast[ -]paced|digital|interconnected|modern) (?:world|landscape|era)\b", "right now", re.IGNORECASE),
            (r"\bfast[ -]paced world\b", "modern work", re.IGNORECASE),
            (r"\b(?:let's|let us) dive in\b", "here is the breakdown", re.IGNORECASE),
            (r"\bdelve into\b", "explore", re.IGNORECASE),
            (r"\bdelve\b", "examine", re.IGNORECASE),
            (r"\bgame[ -]changer\b", "major step forward", re.IGNORECASE),
            (r"\brevolutionize\b", "transform", re.IGNORECASE),
            (r"\belevate\b", "improve", re.IGNORECASE),
            (r"\bfoster\b", "build", re.IGNORECASE),
            (r"\bseamlessly?\b", "smoothly", re.IGNORECASE),
            (r"\bunlock (?:the|your) (?:power|potential)\b", "get the most out of", re.IGNORECASE),
            (r"\bsupercharge\b", "boost", re.IGNORECASE),
            (r"\bcutting[ -]edge\b", "modern", re.IGNORECASE),
            (r"\bdemystify\b", "break down", re.IGNORECASE),
            (r"\ba testament to\b", "clear proof of", re.IGNORECASE),
            (r"\btestament\b", "proof", re.IGNORECASE),
            (r"\bplethora\b", "lot", re.IGNORECASE),
            (r"\bparadigm shift\b", "fresh direction", re.IGNORECASE),
            (r"\blook no further\b", "start right here", re.IGNORECASE),
            (r"\bat the end of the day\b", "ultimately", re.IGNORECASE),
            (r"আজকের (?:দ্রুত পরিবর্তনশীল|ডিজিটাল|আধুনিক|প্রতিযোগিতামূলক) (?:বিশ্বে|যুগে|দুনিয়ায়|সময়ে)", "বর্তমান সময়ে", 0),
            (r"আসুন এক নজরে দেখে নেওয়া যাক", "চলুন দেখি", 0),
            (r"(?:সাফল্যের|সফলতার) (?:মূল )?চাবিকাঠি", "সফল হওয়ার উপায়", 0),
            (r"নিচে (?:বিস্তারিত )?আলোচনা করা হলো", "এখানে বিস্তারিত তুলে ধরা হলো", 0),
            (r"আসুন জেনে (?:নিই|নেওয়া যাক|নেব|নেয়া যাক)", "চলুন জেনে নিই", 0),
            (r"চলুন জেনে (?:নিই|নেওয়া যাক|নেব|নেয়া যাক)", "চলুন দেখি", 0),
            (r"গুরুত্ব অপরিসীম", "খুবই জরুরি", 0),
            (r"বৈপ্লবিক (?:পদক্ষেপ|পরিবর্তন)", "বড় পরিবর্তন", 0),
        ]
        for pattern, rep, flags in cliche_replacements:
            text = re.sub(pattern, rep, text, flags=flags)

        # 4. Platform formatting & hooks
        if plat_val in ("threads", "meta_threads"):
            if not text.endswith("?"):
                text += "\n\nWhat has been your experience with this?"
            if links:
                text += f"\n\n(Full link shared in reply below 💬)"
            if len(text) > 490:
                text = text[:480].rsplit(" ", 1)[0] + "...\n\n(Continued in reply 1/2)"

        elif plat_val in ("instagram", "ig"):
            text += "\n\nSave this for your next project 📌 or send it to a friend."
            if links:
                text += "\n🔗 Link in bio!"
            existing_tags = extract_hashtags(text)
            if len(existing_tags) < 3:
                text += "\n\n#socialgrowth #buildinpublic #creatorinsights"

        elif plat_val in ("twitter", "x"):
            if links:
                text += "\n\n(Link in reply below 🧵)"
            if len(text) > 280:
                parts = []
                cur = ""
                for sent in text.split(". "):
                    if len(cur) + len(sent) < 240:
                        cur += (sent + ". ")
                    else:
                        parts.append(cur.strip())
                        cur = sent + ". "
                if cur.strip():
                    parts.append(cur.strip())
                text = "\n\n---\n\n".join(f"{i+1}/{len(parts)} {p}" for i, p in enumerate(parts))

        elif plat_val == "linkedin":
            if not text.endswith("?"):
                text += "\n\nCurious to hear your thoughts—how do you approach this in your team?"
            if links:
                link_list = ", ".join(links[:2])
                text += f"\n\n💬 P.S. The full link ({link_list}) is in the first comment below to protect reach."

        else:  # Facebook
            if not text.endswith("?"):
                text += "\n\nWhat do you think about this? Let me know your thoughts in the comments."
            if links:
                text += "\n\n(Link in the first comment below 💬)"

        return text.strip()

    def generate(
        self, draft: str, platform: Platform = Platform.FACEBOOK
    ) -> Tuple[str, MetricReport]:
        """
        Calls the configured LLM API (if reachable), then runs deterministic scoring.
        If the API call fails or is offline, transforms the draft using the offline
        rule-based humanizer engine.
        """
        plat_val = platform.value if isinstance(platform, Platform) else str(platform).lower()
        payload = self.build_prompt_payload(draft, platform)
        generated_text = ""

        try:
            import requests

            url = f"{self.api_base.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                generated_text = data["choices"][0]["message"]["content"].strip()
            else:
                generated_text = self.rewrite_offline(draft, platform)
        except Exception:
            generated_text = self.rewrite_offline(draft, platform)

        report = evaluate_text(generated_text, platform=plat_val)
        return generated_text, report
