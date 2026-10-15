"""
Demo launcher for Social-Humanizer Web Playground.
Forwards execution to examples.app
"""

import sys
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.app import run_server, main

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Social-Humanizer Web Playground")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7860, help="Port (default: 7860)")
    parser.add_argument("--gradio", action="store_true", help="Launch Gradio UI if installed")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, use_gradio=args.gradio)
