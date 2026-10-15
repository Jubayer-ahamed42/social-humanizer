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
)
from .engine import HumanizerEngine, Platform

__all__ = [
    "evaluate_text",
    "MetricReport",
    "AlgorithmAudit",
    "AlgorithmWarning",
    "audit_algorithm",
    "HumanizerEngine",
    "Platform",
]
