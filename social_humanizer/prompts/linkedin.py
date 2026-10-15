"""
LinkedIn-specific humanized prompt template.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT

LINKEDIN_PROMPT = BASE_HUMANIZE_PROMPT + """
# LinkedIn Adaptation Guidelines
1. **Culture & Context**:
   - LinkedIn is a professional network where people value clear lessons, career observations, and industry insights.
   - Do NOT humblebrag ("Delighted to share", "Humbled to announce"). Avoid fake drama. Focus on providing real, tangible value to the reader.
2. **Formatting & Readability**:
   - Skimmable: Keep paragraphs concise (1-2 sentences), but avoid extreme 1-line melodrama across every single line.
   - Clear sections: Use simple text separators or plain numbers (1, 2, 3) instead of emoji bullets.
   - Hashtags: 2 to 3 targeted, relevant industry hashtags at the very bottom.
3. **The Hook & Ending**:
   - Hook: First 1-2 lines must hook the reader's curiosity before the "see more" cutoff. Focus on a non-obvious lesson or counter-intuitive experience.
   - Ending: End with an open-ended professional reflection that invites peers to discuss their workflow or experience.

# Goal
Rewrite the user's input into a clean, compelling, humanized LinkedIn post following all guidelines above.
"""
