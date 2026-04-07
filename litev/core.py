import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

@dataclass
class Config:
    """Configuration for the audit process.

    Attributes:
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.
        log_file: Path for JSONL audit logs.
        model_provider: Provider name ("stub", "bedrock", etc.).
        model_name: Model identifier (provider-specific).
    """
    chunk_size: int = 1024
    chunk_overlap: int = 200
    log_file: Path = Path("results.jsonl")
    model_provider: str = "stub"    # "stub", "bedrock"
    model_name: str = "gpt-4o-mini"

@dataclass
class Data:
    """The document to be audited.

    Attributes:
        text: The raw text content.
        metadata: Optional metadata for logging.
    """
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Chunk:
    """A piece of the original document.

    Attributes:
        index: Zero-based chunk index.
        text: The chunk's text content.
        passed: Audit result (True/False/None).
        raw_resp: Raw response from the model provider.
    """
    index: int
    text: str
    passed: Optional[bool] = None
    raw_resp: Optional[str] = None

@dataclass
class Rubric:
    """The rule-set (ground truth) for evaluation.

    Attributes:
        text: Plain-text rubric describing the required criteria.
    """
    text: str

class ScoreStrategy(ABC):
    """Abstract base class for scoring strategies.

    Subclass this to implement custom scoring logic.
    """
    @abstractmethod
    def compute(self, chunks: List[Chunk]) -> float:
        """Return a score in [0.0, 1.0] based on the audit results."""
        pass

class PassRateStrategy(ScoreStrategy):
    """Simple scoring strategy: fraction of passing chunks."""
    def compute(self, chunks: List[Chunk]) -> float:
        valid = [c for c in chunks if c.passed is not None]
        if not valid:
            return 0.0
        return sum(1 for c in valid if c.passed) / len(valid)

def chunk_document(data: Data, config: Config) -> List[Chunk]:
    """Split the document into overlapping chunks according to the configuration.

    Returns:
        List[Chunk]: The chunked document.
    Raises:
        ValueError: If chunk_size <= chunk_overlap.
    """
    chunks = []
    text = data.text
    step = config.chunk_size - config.chunk_overlap
    if step <= 0:
        raise ValueError("chunk_size must be greater than chunk_overlap")
    for i in range(0, len(text), step):
        end = min(i + config.chunk_size, len(text))
        chunk_text = text[i:end]
        chunks.append(Chunk(index=len(chunks), text=chunk_text))
    return chunks

async def audit_chunk(chunk: Chunk, rubric: Rubric, config: Config) -> None:
    """Evaluate a single chunk against the rubric.

    This is a stub implementation that always marks chunks as passed.
    Override this function to integrate with a real model provider.
    """
    chunk.passed = True
    chunk.raw_resp = "stubbed: always compliant"

async def run_audit(
    data: Data,
    rubric: Rubric,
    config: Config,
    score_strategy: ScoreStrategy,
) -> float:
    """Orchestrate the entire audit process.

    Steps:
        1. Chunk the document.
        2. Evaluate each chunk against the rubric.
        3. Compute the final score using the provided strategy.

    Returns:
        float: The final compliance score between 0.0 and 1.0.
    """
    chunks = chunk_document(data, config)
    for chunk in chunks:
        await audit_chunk(chunk, rubric, config)
    final_score = score_strategy.compute(chunks)
    return final_score
