"""
Core Humanizer Engine coordinating prompt generation, optional LLM generation,
and deterministic metric scoring.
"""

from enum import Enum
import json
import os
from typing import Dict, Any, Optional, Tuple

from .metrics import evaluate_text, MetricReport
from .prompts.facebook import FACEBOOK_PROMPT
from .prompts.linkedin import LINKEDIN_PROMPT
from .prompts.twitter import TWITTER_PROMPT


class Platform(str, Enum):
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


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
        if platform == Platform.FACEBOOK:
            return FACEBOOK_PROMPT
        elif platform == Platform.LINKEDIN:
            return LINKEDIN_PROMPT
        elif platform == Platform.TWITTER:
            return TWITTER_PROMPT
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

    def generate(
        self, draft: str, platform: Platform = Platform.FACEBOOK
    ) -> Tuple[str, MetricReport]:
        """
        Calls the configured LLM API (if reachable), then runs deterministic scoring.
        If the API call fails or is offline, falls back to generating a helpful blueprint.
        """
        payload = self.build_prompt_payload(draft, platform)
        generated_text = ""

        try:
            import requests

            url = f"{self.api_base.rstrip('/')}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                generated_text = data["choices"][0]["message"]["content"].strip()
            else:
                generated_text = (
                    f"⚠️ LLM API returned status {resp.status_code}. "
                    f"Please check your API key or local model endpoint."
                )
        except Exception as e:
            generated_text = (
                f"ℹ️ [Offline Mode / No LLM Connected]\n"
                f"You can use this structured prompt with your preferred AI:\n\n"
                f"--- SYSTEM PROMPT ---\n{payload['messages'][0]['content']}\n\n"
                f"--- USER PROMPT ---\n{payload['messages'][1]['content']}"
            )

        report = evaluate_text(generated_text)
        return generated_text, report
