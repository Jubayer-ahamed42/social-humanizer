"""
Facebook-specific humanized prompt template.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT

FACEBOOK_PROMPT = BASE_HUMANIZE_PROMPT + """
# Facebook Adaptation Guidelines
1. **Culture & Context**:
   - Facebook is a relaxed, social space for friends, family, and community discussions.
   - Do NOT sound like a LinkedIn thought leader or a marketer. Sound like a curious, thoughtful friend.
2. **Formatting**:
   - Use natural 2-3 sentence paragraph blocks.
   - Do NOT use LinkedIn-style double-spaced single-sentence lines (Broetry).
   - Emojis: Maximum 1 or 2 subtle emojis (e.g. 😅 or 🤔) placed naturally at the end, or zero.
   - Hashtags: Maximum 0 to 1 natural hashtag (never a cluster of hashtags).
3. **The Hook & Ending**:
   - Hook: Start with a relatable real-life situation, unexpected thought, or a personal dilemma ("আজকে একটা অদ্ভুত জিনিস খেয়াল করলাম...", "I noticed something strange today...").
   - Ending: Close with a low-friction, genuine question that makes friends want to comment and share their perspective.

# Goal
Rewrite the user's input into a humanized Facebook post following all the guidelines above.
"""
