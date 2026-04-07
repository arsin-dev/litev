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
    register_provider,
    get_provider,
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
    "register_provider",
    "get_provider",
]

__version__ = "0.1.0"