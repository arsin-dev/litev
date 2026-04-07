#!/usr/bin/env python3
"""Basic usage example for LiteV."""

import asyncio
from typing import List
from litev import (
    Config,
    Data,
    Rubric,
    Chunk,
    ScoreStrategy,
    PassRateStrategy,
    run_audit,
)


class SimpleThresholdStrategy(ScoreStrategy):
    """Require at least 70% of chunks to pass."""
    def compute(self, chunks: List[Chunk]) -> float:
        valid = [c for c in chunks if c.passed is not None]
        if not valid:
            return 0.0
        pass_rate = sum(1 for c in valid if c.passed) / len(valid)
        return 1.0 if pass_rate >= 0.7 else pass_rate


async def main():
    # Example: checking a software license agreement
    license_text = """
    MIT License
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    """
    
    rubric_text = """
    The license must:
    1. Be an open-source license.
    2. Include a disclaimer of warranty.
    3. Include a limitation of liability.
    4. Allow modification and distribution.
    """
    
    config = Config(chunk_size=500, chunk_overlap=100)
    
    # Strategy 1: Simple pass rate
    strategy1 = PassRateStrategy()
    
    # Strategy 2: Threshold-based
    strategy2 = SimpleThresholdStrategy()
    
    data = Data(text=license_text)
    rubric = Rubric(text=rubric_text)
    
    score1 = await run_audit(data, rubric, config, strategy1)
    score2 = await run_audit(data, rubric, config, strategy2)
    
    print(f"License compliance (pass rate): {score1:.2f}")
    print(f"License compliance (threshold): {score2:.2f}")
    print("\nNote: The stub provider always returns 'passed=True',")
    print("so scores will be 1.0 until you integrate a real model provider.")


if __name__ == "__main__":
    asyncio.run(main())