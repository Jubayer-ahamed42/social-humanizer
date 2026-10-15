import sys
from pathlib import Path

# Add project root to sys.path so demo runs directly without install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from social_humanizer.engine import HumanizerEngine, Platform

def main():
    engine = HumanizerEngine()
    topic = "The hidden truth about junior developer burnout in tech."
    
    print(f"Topic: {topic}\n")
    payload = engine.build_prompt_payload(topic, platform=Platform.INSTAGRAM)
    
    print("=== System Prompt (Instagram Caption Humanizer) ===")
    print(payload["messages"][0]["content"][:450] + "...\n[Full prompt continues]")
    
    print("\n=== User Prompt ===")
    print(payload["messages"][1]["content"])

if __name__ == "__main__":
    main()
