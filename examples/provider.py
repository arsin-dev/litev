"""Example of using OpenRouter provider with LiteV.

Make sure you have installed the optional dependencies:
    pip install litev[openai]

Set your OpenRouter API key as environment variable:
    export OPENROUTER_API_KEY=sk-or-...

Run this example:
    python provider.py
"""

import asyncio
import os
from litev import Config, Data, Rubric, PassRateStrategy, run_audit
from litev.providers import register_openrouter

async def main():
    register_openrouter()

    document = """
    This software is provided as-is, without any warranties.
    The author is not liable for any damages.
    You may use, modify, and distribute this software freely.
    """
    rubric = Rubric(text="""
    The text must:
    1. Include a disclaimer of warranty.
    2. Include a limitation of liability.
    3. Allow modification and distribution.
    """)

    config = Config(
        chunk_size=500,
        chunk_overlap=100,
        model_provider="openrouter",
        # model_name can be omitted to use the default free model
    )

    data = Data(text=document)
    strategy = PassRateStrategy()

    print("Running audit with OpenRouter provider...")
    score = await run_audit(data, rubric, config, strategy)
    print(f"Compliance score: {score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())