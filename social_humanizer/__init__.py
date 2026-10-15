"""
Social-Humanizer: Universal AI Social Media Humanizer & Quality Scorer
"""

__version__ = "0.2.0"
__author__ = "Social-Humanizer Contributors"

from .metrics import (
    evaluate_text,
    MetricReport,
    AlgorithmAudit,
    AlgorithmWarning,
    audit_algorithm,
    extract_emojis,
    calculate_shannon_entropy,
    analyze_hook,
    HookAnalysis,
)
from .engine import HumanizerEngine, Platform

__all__ = [
    "evaluate_text",
    "MetricReport",
    "AlgorithmAudit",
    "AlgorithmWarning",
    "audit_algorithm",
    "extract_emojis",
    "calculate_shannon_entropy",
    "analyze_hook",
    "HookAnalysis",
    "HumanizerEngine",
    "Platform",
]

