import asyncio
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from litev import (
    Config, Data, Chunk, Rubric,
    ScoreStrategy, PassRateStrategy,
    chunk_document, audit_chunk, run_audit
)

class WeightedByKeywordStrategy(ScoreStrategy):
    def __init__(self, keyword_weights: dict):
        self.keyword_weights = keyword_weights

    def compute(self, chunks: List[Chunk]) -> float:
        total_weight = 0.0
        weighted_pass = 0.0
        for chunk in chunks:
            weight = 0.0
            for kw, w in self.keyword_weights.items():
                if kw.lower() in chunk.text.lower():
                    weight = w
                    break
            if weight == 0.0:
                weight = 0.2
            total_weight += weight
            if chunk.passed:
                weighted_pass += weight
        return weighted_pass / total_weight if total_weight > 0 else 0.0

async def main():
    policy_text = """
    SECTION 1: LIABILITY COVERAGE
    We will pay damages for bodily injury or property damage for which you become legally
    responsible because of an auto accident. The limit is $100,000 per person.

    SECTION 2: COLLISION DEDUCTIBLE
    For collision coverage, a $500 deductible applies per occurrence.

    SECTION 3: EXCLUSIONS
    This policy does not cover:
    - Intentional damage
    - Wear and tear
    - Racing activities
    """

    rubric_text = """
    The policy must:
    1. Provide liability coverage with minimum $50,000 per person.
    2. Include a deductible clause for collision (any amount is fine).
    3. Exclude racing activities explicitly.
    """

    config = Config(chunk_size=300, chunk_overlap=50)

    # Custom scoring: critical chunks are those with 'liability', 'deductible', 'exclusion'
    keyword_weights = {
        "liability": 0.5,
        "deductible": 0.3,
        "exclusion": 0.4
    }
    strategy = WeightedByKeywordStrategy(keyword_weights)

    data = Data(text=policy_text)
    rubric = Rubric(text=rubric_text)

    score = await run_audit(data, rubric, config, strategy)
    print(f"Insurance compliance score: {score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())