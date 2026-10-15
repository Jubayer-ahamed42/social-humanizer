"""
Command Line Interface for Social-Humanizer.
Provides interactive scoring and prompt generation.
"""

import argparse
import sys
from typing import Optional

# Ensure UTF-8 output encoding across Windows and non-UTF-8 terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .metrics import evaluate_text
from .engine import HumanizerEngine, Platform

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False


def print_rich_report(report) -> None:
    """Renders a beautiful terminal report card using Rich."""
    color = "green" if report.is_human_sounding else "yellow"
    if report.human_score < 50:
        color = "red"

    status_str = "✅ Human-Sounding" if report.is_human_sounding else "⚠️ Robotic / Needs Polish"

    table = Table(title="📊 Text Quality & Cadence Analysis", border_style=color)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    table.add_column("Assessment", style="magenta")

    table.add_row(
        "Human Score",
        f"{report.human_score:.1f} / 100",
        status_str,
    )
    table.add_row(
        "Burstiness (CV)",
        f"{report.burstiness_score:.2f}",
        "High variance (Good)" if report.burstiness_score >= 0.4 else "Low variance (Monotonous)",
    )
    table.add_row(
        "Word & Sentence Count",
        f"{report.word_count} words, {report.sentence_count} sentences",
        f"Avg ~{report.avg_sentence_length:.1f} words/sentence",
    )
    table.add_row(
        "Readability Level",
        f"Flesch: {report.reading_ease:.1f}",
        report.grade_level,
    )

    console.print(table)

    if report.flagged_cliches:
        console.print(
            Panel(
                f"[bold red]Flagged AI Clichés:[/bold red] {', '.join(report.flagged_cliches)}",
                title="🚨 Cliché Blacklist",
                border_style="red",
            )
        )
    if report.has_emoji_spam:
        console.print(
            Panel(
                "[bold yellow]Emoji bullet spam detected.[/bold yellow] Avoid starting lines with 🚀, 🔥, 💡.",
                title="⚠️ Formatting Warning",
                border_style="yellow",
            )
        )
    if report.recommendations:
        recs = "\n".join(f"• {r}" for r in report.recommendations)
        console.print(Panel(recs, title="💡 Actionable Recommendations", border_style="blue"))


def print_plain_report(report) -> None:
    """Renders plain text report when Rich is not installed."""
    print("=" * 60)
    print(report.summary())
    print("=" * 60)


def cmd_score(args) -> None:
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()

    if not text:
        print("Error: No text provided to score. Use text argument or --file.")
        sys.exit(1)

    report = evaluate_text(text)
    if HAS_RICH and console:
        print_rich_report(report)
    else:
        print_plain_report(report)


def cmd_prompt(args) -> None:
    platform = Platform(args.platform.lower())
    engine = HumanizerEngine()
    prompt = engine.get_system_prompt(platform)
    print(f"=== SYSTEM PROMPT FOR {platform.value.upper()} ===")
    print(prompt)


def cmd_run(args) -> None:
    platform = Platform(args.platform.lower())
    engine = HumanizerEngine(
        api_base=args.api_base,
        api_key=args.api_key,
        model=args.model,
    )
    output, report = engine.generate(args.draft, platform=platform)
    print("\n=== GENERATED / STRUCTURED OUTPUT ===")
    print(output)
    print("\n=== EVALUATION REPORT ===")
    if HAS_RICH and console:
        print_rich_report(report)
    else:
        print_plain_report(report)


def main():
    parser = argparse.ArgumentParser(
        prog="social-humanizer",
        description="Universal AI Social Media Humanizer & Quality Scorer",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Score command
    score_p = subparsers.add_parser("score", help="Score text for humanization and burstiness")
    score_p.add_argument("text", nargs="?", default="", help="Text to evaluate")
    score_p.add_argument("-f", "--file", help="Path to file containing text to evaluate")
    score_p.set_defaults(func=cmd_score)

    # Prompt command
    prompt_p = subparsers.add_parser("prompt", help="Display system prompt for a platform")
    prompt_p.add_argument(
        "-p", "--platform",
        choices=["facebook", "linkedin", "twitter"],
        default="facebook",
        help="Target social media platform",
    )
    prompt_p.set_defaults(func=cmd_prompt)

    # Run command
    run_p = subparsers.add_parser("run", help="Run humanizer on a draft")
    run_p.add_argument("draft", help="Raw draft topic or text")
    run_p.add_argument(
        "-p", "--platform",
        choices=["facebook", "linkedin", "twitter"],
        default="facebook",
    )
    run_p.add_argument("--api-base", help="Custom OpenAI-compatible API base URL")
    run_p.add_argument("--api-key", help="API key")
    run_p.add_argument("--model", help="Model name (e.g. llama3, gemini-1.5-flash)")
    run_p.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
