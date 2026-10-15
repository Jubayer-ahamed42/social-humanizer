"""
Command Line Interface for Social-Humanizer.
Provides rich interactive scoring, anti-AI algorithmic risk auditing, and prompt generation.
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

from .metrics import evaluate_text, MetricReport
from .engine import HumanizerEngine, Platform

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

SUPPORTED_PLATFORMS = ["facebook", "linkedin", "twitter", "threads", "instagram"]


def render_burstiness_meter(cv: float) -> str:
    """Renders a visual meter for Coefficient of Variation (CV)."""
    total_blocks = 10
    filled = min(total_blocks, max(0, int(round((cv / 0.50) * total_blocks))))
    empty = total_blocks - filled
    bar = "█" * filled + "░" * empty
    if cv >= 0.45:
        return f"[bold green]{bar}[/bold green] {cv:.2f} (Dynamic Human Cadence)"
    elif cv >= 0.35:
        return f"[bold yellow]{bar}[/bold yellow] {cv:.2f} (Moderate Cadence)"
    else:
        return f"[bold red]{bar}[/bold red] {cv:.2f} (Monotonous AI Pattern)"


def print_rich_report(report: MetricReport, platform: Optional[str] = None) -> None:
    """Renders a visually stunning terminal report card and algorithmic audit dashboard using Rich."""
    # Determine scorecard theme
    if report.human_score >= 70.0 and report.algorithm_risk_score < 25.0:
        theme_color = "green"
        status_badge = "[bold white on green]  AUTHENTIC HUMAN • VIRAL-READY  [/bold white on green]"
    elif report.human_score >= 50.0 and report.algorithm_risk_score < 60.0:
        theme_color = "yellow"
        status_badge = "[bold black on yellow]  MODERATE RISK • POLISH NEEDED  [/bold black on yellow]"
    else:
        theme_color = "red"
        status_badge = "[bold white on red]  AI DETECTED • HIGH ALGORITHM PENALTY  [/bold white on red]"

    platform_tag = f" • Platform: [bold cyan]{platform.upper()}[/bold cyan]" if platform else ""
    header_content = (
        f"{status_badge}{platform_tag}\n\n"
        f"• [bold]Human Score:[/bold] [{theme_color}]{report.human_score:.1f} / 100[/{theme_color}]  "
        f"• [bold]Algo Penalty Risk:[/bold] [{theme_color}]{report.algorithm_risk_score:.0f} / 100 ({report.algorithm_risk_level})[/{theme_color}]"
    )
    console.print(Panel(header_content, title="🚀 [bold]Social-Humanizer Quality Dashboard[/bold]", border_style=theme_color))

    # Core Metrics Table
    table = Table(title="📊 [bold]Syntactic, Readability & Distribution Metrics[/bold]", border_style=theme_color, show_lines=True)
    table.add_column("Metric", style="bold cyan", width=24)
    table.add_column("Value", style="bold white", width=30)
    table.add_column("Benchmark Target", style="dim white", width=22)
    table.add_column("Status Assessment", width=30)

    # 1. Human Score
    score_status = f"[green]Passed[/green]" if report.human_score >= 70 else (f"[yellow]Borderline[/yellow]" if report.human_score >= 50 else f"[red]Critical AI Markers[/red]")
    table.add_row("Human Quality Score", f"{report.human_score:.1f} / 100", "≥ 70.0 pts", score_status)

    # 2. Burstiness CV
    burst_meter = render_burstiness_meter(report.burstiness_score)
    burst_status = "[green]High sentence variety[/green]" if report.burstiness_score >= 0.45 else ("[yellow]Moderate variety[/yellow]" if report.burstiness_score >= 0.35 else "[red]Monotonous cadence[/red]")
    table.add_row("Burstiness (Cadence CV)", burst_meter, "CV ≥ 0.45", burst_status)

    # 3. Reading Ease & Level
    read_status = "[green]Optimal for Social[/green]" if report.reading_ease >= 60 else "[yellow]Dense / Academic[/yellow]"
    table.add_row("Reading Ease (Flesch)", f"{report.reading_ease:.1f} ({report.grade_level})", "60 – 85 (Grade 6-8)", read_status)

    # 4. Word & Sentence Counts
    table.add_row(
        "Content Structure",
        f"{report.word_count} words | {report.sentence_count} sentences",
        "Varied lengths",
        f"Avg ~{report.avg_sentence_length:.1f} words/sentence",
    )

    # 5. Outbound Links
    link_status = "[red]High reach suppression (50%-80%)[/red]" if report.has_external_links else "[green]Safe (Zero reach penalty)[/green]"
    link_val = f"{len(report.external_links)} outbound link(s)" if report.has_external_links else "0 links detected"
    table.add_row("Outbound Links (Body)", link_val, "0 in body (use 1st comment)", link_status)

    # 6. Hashtags
    tag_status = "[red]Hashtag spam penalty[/red]" if report.has_excessive_hashtags else "[green]Healthy tag density[/green]"
    tag_val = f"{report.hashtag_count} tag(s)" if report.hashtag_count > 0 else "0 tags"
    table.add_row("Hashtag Density", tag_val, "0 – 3 tags max", tag_status)

    console.print(table)

    # Algorithmic Auditor Warnings
    if report.audit and report.audit.warnings:
        warn_table = Table(title="🛡️ [bold red]Algorithmic Risk Auditor Warnings[/bold red]", border_style="red", show_lines=True)
        warn_table.add_column("Category", style="bold yellow", width=22)
        warn_table.add_column("Severity", width=12)
        warn_table.add_column("Algorithmic Impact & Actionable Solution", width=70)

        for w in report.audit.warnings:
            if w.severity == "high":
                sev_badge = f"[bold white on red] {w.severity.upper()} [/bold white on red]"
            elif w.severity == "medium":
                sev_badge = f"[bold black on yellow] {w.severity.upper()} [/bold black on yellow]"
            else:
                sev_badge = f"[bold white on blue] {w.severity.upper()} [/bold white on blue]"
            impact_text = f"[bold]{w.message}[/bold]\n[dim cyan]↳ Fix: {w.recommendation}[/dim cyan]"
            warn_table.add_row(w.category, sev_badge, impact_text)

        console.print(warn_table)

    # Flagged Clichés Highlights
    if report.flagged_cliches:
        badges = "  ".join(f"[bold white on red] ✖ {c} [/bold white on red]" for c in report.flagged_cliches)
        cliche_content = (
            f"[bold]Detected blacklisted AI buzzwords and corporate jargon:[/bold]\n\n"
            f"{badges}\n\n"
            f"[dim]These phrases immediately flag your text to social ranking algorithms and AI detectors. Replace with grounded human language.[/dim]"
        )
        console.print(Panel(cliche_content, title="🚨 [bold red]Flagged AI Clichés Blacklist[/bold red]", border_style="red"))

    # Recommendations
    if report.recommendations:
        recs_formatted = "\n".join(f"[bold green]✔[/bold green] {r}" for r in report.recommendations)
        console.print(Panel(recs_formatted, title="💡 [bold cyan]Actionable Improvement Plan[/bold cyan]", border_style="cyan"))


def print_plain_report(report: MetricReport, platform: Optional[str] = None) -> None:
    """Renders plain text report when Rich is not installed."""
    print("=" * 65)
    if platform:
        print(f"Target Platform: {platform.upper()}")
    print(report.summary())
    if report.audit and report.audit.warnings:
        print("\nAlgorithmic Auditor Warnings:")
        for w in report.audit.warnings:
            print(f" [{w.severity.upper()}] {w.category}: {w.message}")
            print(f"     ↳ Fix: {w.recommendation}")
    print("=" * 65)


def cmd_score(args) -> None:
    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    elif not text and not sys.stdin.isatty():
        try:
            text = sys.stdin.read().strip()
        except Exception:
            text = ""

    if not text:
        print("Error: No text provided to score. Use text argument, --file, or pipe via stdin.")
        sys.exit(1)

    plat = args.platform.lower() if args.platform else None
    report = evaluate_text(text, platform=plat)

    if HAS_RICH and console:
        print_rich_report(report, platform=plat)
    else:
        print_plain_report(report, platform=plat)


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
        print_rich_report(report, platform=platform.value)
    else:
        print_plain_report(report, platform=platform.value)


def main():
    parser = argparse.ArgumentParser(
        prog="social-humanizer",
        description="Universal AI Social Media Humanizer & Algorithmic Risk Auditor",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Score command
    score_p = subparsers.add_parser("score", help="Score text for humanization and algorithmic risk")
    score_p.add_argument("text", nargs="?", default="", help="Text to evaluate")
    score_p.add_argument("-f", "--file", help="Path to file containing text to evaluate")
    score_p.add_argument(
        "-p", "--platform",
        choices=SUPPORTED_PLATFORMS,
        default=None,
        help="Optional target platform (facebook, linkedin, twitter, threads, instagram) for platform-specific audit",
    )
    score_p.set_defaults(func=cmd_score)

    # Prompt command
    prompt_p = subparsers.add_parser("prompt", help="Display system prompt for a platform")
    prompt_p.add_argument(
        "-p", "--platform",
        choices=SUPPORTED_PLATFORMS,
        default="facebook",
        help="Target social media platform",
    )
    prompt_p.set_defaults(func=cmd_prompt)

    # Run command
    run_p = subparsers.add_parser("run", help="Run humanizer on a draft")
    run_p.add_argument("draft", help="Raw draft topic or text")
    run_p.add_argument(
        "-p", "--platform",
        choices=SUPPORTED_PLATFORMS,
        default="facebook",
        help="Target social media platform",
    )
    run_p.add_argument("--api-base", help="Custom OpenAI-compatible API base URL")
    run_p.add_argument("--api-key", help="API key")
    run_p.add_argument("--model", help="Model name (e.g. llama3, gemini-1.5-flash)")
    run_p.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
