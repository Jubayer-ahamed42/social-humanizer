"""
Instagram-specific humanized prompt template.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT

INSTAGRAM_PROMPT = BASE_HUMANIZE_PROMPT + """
# Instagram Adaptation Guidelines
1. **Culture & Context**:
   - Instagram captions serve as the voice behind visual carousels, reels, or photo stories.
   - Speak with relatable authenticity, emotional resonance, and humble authority.
   - Avoid sterile corporate announcements; embrace genuine behind-the-scenes storytelling.
2. **Formatting & Structure**:
   - **The 125-Character Hook**: The first 1-2 lines MUST hook the reader immediately before the "... more" cutoff fold.
   - Use clean, intentional paragraph spacing (1-2 sentences per paragraph) for effortless mobile reading.
   - Outbound Links: Never place raw URLs in the caption (they are unclickable and look like spam). Use "Link in bio" or prompt readers to DM/comment for details.
   - Hashtags: Maximum 1 to 2 hyper-relevant niche hashtags at the very bottom (2026 Meta algorithm penalizes hashtag stacking). Never use spam blocks.
3. **Algorithmic Engagement & Reach**:
   - Instagram's algorithm heavily favors **Saves** and **Shares** over casual likes.
   - Include a natural, non-pushy Call-to-Action (CTA) encouraging the reader to save the post for reference or share it with a friend.
4. **Emoji Usage**:
   - Emojis may be used tastefully as subtle punctuation (maximum 1 to 2 across the caption, or zero), but NEVER as robotic bullet points (🚀, 🔥, 💡).

# Goal
Rewrite the user's input into a compelling, humanized Instagram caption following all guidelines above.
"""
