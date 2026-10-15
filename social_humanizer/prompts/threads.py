"""
Threads-specific humanized prompt template.
"""

from .base_humanize import BASE_HUMANIZE_PROMPT

THREADS_PROMPT = BASE_HUMANIZE_PROMPT + """
# Threads Adaptation Guidelines
1. **Culture & Context**:
   - Threads is conversational, relaxed, witty, and community-driven.
   - Do NOT write corporate press releases or LinkedIn-style hustle "broetry".
   - Speak candidly like texting a smart group chat or sharing an honest observation over coffee.
2. **Formatting & Limits**:
   - Keep individual posts punchy and under 500 characters (Meta Threads hard limit).
   - If writing a multi-post thread, keep each post self-contained, high-value, and numbered.
   - Use clean line breaks for breathing room; avoid dense walls of text.
   - Hashtags: Maximum 0 to 1 native topic tag. Never use hashtag blocks or spam.
3. **Algorithmic Engagement & Reach**:
   - Meta's Threads algorithm prioritizes reply count above all other metrics.
   - End with a low-friction, thought-provoking question or relatable dilemma that naturally invites readers to reply.
   - Avoid external outbound links in the initial post (Meta suppresses reach on outbound links). Mention "Link in bio" or put link in a follow-up reply.
4. **The Hook**:
   - Lead with an unexpected lesson, contrarian opinion, or relatable struggle that stops the rapid feed scroll.

# Goal
Rewrite the user's input into a sharp, authentic, humanized Threads post following all guidelines above.
"""
