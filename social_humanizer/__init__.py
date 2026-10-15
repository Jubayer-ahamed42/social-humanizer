"""
Social-Humanizer: Universal AI Social Media Humanizer & Quality Scorer
"""

__version__ = "0.1.0"
__author__ = "Social-Humanizer Contributors"

from .metrics import evaluate_text, MetricReport
from .engine import HumanizerEngine, Platform

__all__ = [
    "evaluate_text",
    "MetricReport",
    "HumanizerEngine",
    "Platform",
]
