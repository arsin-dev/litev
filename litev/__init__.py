"""
LiteV - A lightweight, extensible vetting/auditing system.
"""

from .core import (
    Config,
    Data,
    Chunk,
    Rubric,
    ScoreStrategy,
    PassRateStrategy,
    chunk_document,
    audit_chunk,
    run_audit,
)

__all__ = [
    "Config",
    "Data",
    "Chunk",
    "Rubric",
    "ScoreStrategy",
    "PassRateStrategy",
    "chunk_document",
    "audit_chunk",
    "run_audit",
]

__version__ = "0.1.0"