"""OpenRouter provider for LiteV."""

import os
import json
from typing import Optional
from ..core import Chunk, Rubric, Config

# OpenAI import is deferred to the provider function to allow optional installation

# Default model (free on OpenRouter; may be rate‑limited)
# See https://openrouter.ai/models for other free/paid models.
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"

# OpenRouter base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def _get_api_key() -> Optional[str]:
    """Retrieve OpenRouter API key from environment."""
    return os.environ.get("OPENROUTER_API_KEY")

async def openrouter_provider(
    chunk: Chunk,
    rubric: Rubric,
    config: Config,
) -> tuple[bool, str]:
    """Evaluate a chunk using OpenRouter.

    Args:
        chunk: The text chunk to evaluate.
        rubric: The rubric describing the criteria.
        config: Audit configuration (model_name used).

    Returns:
        Tuple of (passed: bool, raw_response: str).
    """
    # Deferred import to allow optional installation
    try:
        from openai import AsyncOpenAI
    except ImportError as e:
        raise ImportError(
            "OpenAI package is required for OpenRouter provider. "
            "Install with: pip install litev[openai]"
        ) from e

    api_key = _get_api_key()
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set. "
            "Get an API key from https://openrouter.ai/keys"
        )

    model = config.model_name.strip() or DEFAULT_MODEL

    # Build a simple prompt
    prompt = f"""You are an auditor evaluating text compliance with a rubric.

RUBRIC:
{rubric.text}

CHUNK:
{chunk.text}

Does the chunk comply with the rubric? Answer only with YES or NO."""

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
    )

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise auditor."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=5,
            temperature=0.0,
        )
        raw = response.choices[0].message.content or ""
        raw = raw.strip()
        # Simple parsing
        passed = raw.upper().startswith("YES")
        return passed, json.dumps({
            "model": model,
            "response": raw,
            "usage": response.usage.dict() if response.usage else None,
        })
    except Exception as e:
        # In case of error, treat as failure and include error in raw response
        return False, json.dumps({"error": str(e)})

def register_openrouter():
    """Register the OpenRouter provider with the default name 'openrouter'."""
    from ..core import register_provider
    register_provider("openrouter", openrouter_provider)