"""
Twitter / X-specific humanized prompt template.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT

TWITTER_PROMPT = BASE_HUMANIZE_PROMPT + """
# Twitter / X Adaptation Guidelines
1. **Culture & Context**:
   - Fast, sharp, and concise. No room for filler words.
2. **Formatting**:
   - For single tweets: keep under 280 characters with high impact.
   - For threads: number each tweet (1/n, 2/n) and make each tweet stand alone as a valuable thought.
   - Emojis: Maximum 0 to 1 subtle emoji (never emoji bullets).
   - Hashtags: Maximum 0 to 1 hashtag (never use hashtag dumps).
3. **The Hook**:
   - A bold, concise statement or observation that stops the fast scroll.

# Goal
Rewrite the user's input into a sharp, humanized tweet or short thread following all guidelines above.
"""
