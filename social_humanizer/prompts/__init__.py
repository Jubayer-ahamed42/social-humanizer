"""
Prompts module for Social-Humanizer.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT
from .facebook import FACEBOOK_PROMPT
from .linkedin import LINKEDIN_PROMPT
from .twitter import TWITTER_PROMPT
from .threads import THREADS_PROMPT
from .instagram import INSTAGRAM_PROMPT

__all__ = [
    "BASE_HUMANIZE_PROMPT",
    "FACEBOOK_PROMPT",
    "LINKEDIN_PROMPT",
    "TWITTER_PROMPT",
    "THREADS_PROMPT",
    "INSTAGRAM_PROMPT",
]
