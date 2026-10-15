import os
import sys
from pathlib import Path

# Add project root to sys.path so demo runs directly without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from social_humanizer.metrics import evaluate_text

SAMPLE_ROBOTIC = """
🚀 Elevate your brand today! In today's fast-paced digital landscape, it is crucial to delve into revolutionary technologies. 
💡 Unlock your true potential with our seamless AI platform.
🔥 Here are 3 key takeaways:
- Foster deep relationships
- Maximize your business impact
- Navigate complex market challenges
"""

SAMPLE_HUMAN = """
I noticed something weird about programming yesterday. 
Computers are fundamentally dumb. 
They do exactly what you tell them to do, not what you want them to do. Miss a single semicolon? The entire screen turns red. 
Honestly, who else has lost 4 hours of sleep over a typo?
"""

def main():
    print("--- 1. Evaluating Robotic AI Text ---")
    report1 = evaluate_text(SAMPLE_ROBOTIC)
    print(report1.summary())
    print("\n" + "=" * 50 + "\n")

    print("--- 2. Evaluating Humanized Post ---")
    report2 = evaluate_text(SAMPLE_HUMAN)
    print(report2.summary())

if __name__ == "__main__":
    main()
