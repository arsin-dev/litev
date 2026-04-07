# LiteV

**A lightweight, extensible vetting/auditing system for scoring text documents against rubrics.**

LiteV (`Rubric`, `Data`) → `Score`

LiteV is a dependency-free Python framework for automatically evaluating text documents against rule-based criteria (rubrics). It chunks long documents, evaluates each chunk using pluggable model providers, and aggregates results with customizable scoring strategies—perfect for compliance checking, policy verification, contract auditing, and similar vetting tasks.

## ✨ Features

- **Zero Dependencies** – Core logic is pure Python; no external libraries required.
- **Extensible Architecture** – Plug in your own model providers, chunking algorithms, or scoring strategies.
- **Configurable Chunking** – Adjust chunk size and overlap to balance context preservation with processing efficiency.
- **Async‑Ready** – Built on `asyncio` for concurrent evaluation when using remote model providers.
- **Audit Logging** – All results are written to a JSONL file for traceability and debugging.
- **Custom Scoring** – Simple pass‑rate, weighted‑keyword, or your own scoring logic.

## 📦 Installation

### From Source

Clone the repository and install with `uv` (recommended) or `pip`:

```bash
git clone <repository-url>
cd LiteV

# Using uv
uv pip install -e .

# Using pip
pip install -e .
```

### As a Dependency

Add `litev` to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "litev>=0.1.0",
]
```

Or install directly:

```bash
uv pip install litev
```

**Note:** The core package has zero dependencies. Optional dependencies (e.g., `openai`) must be installed separately if you need them.

## 🚀 Quick Start

Here’s a complete example that checks an auto‑insurance policy against a simple rubric:

```python
import asyncio
from lite_v import (
    Config, Data, Rubric, ScoreStrategy, 
    chunk_document, audit_chunk, run_audit
)
from typing import List

# 1. Define a custom scoring strategy
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
    # 2. The document to audit
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

    # 3. The rubric (ground‑truth rules)
    rubric_text = """
    The policy must:
    1. Provide liability coverage with minimum $50,000 per person.
    2. Include a deductible clause for collision (any amount is fine).
    3. Exclude racing activities explicitly.
    """

    # 4. Configuration
    config = Config(chunk_size=300, chunk_overlap=50)

    # 5. Custom scoring weights for critical keywords
    keyword_weights = {
        "liability": 0.5,
        "deductible": 0.3,
        "exclusion": 0.4
    }
    strategy = WeightedByKeywordStrategy(keyword_weights)

    # 6. Run the audit
    data = Data(text=policy_text)
    rubric = Rubric(text=rubric_text)
    score = await run_audit(data, rubric, config, strategy)
    print(f"Insurance compliance score: {score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python examples/insurance.py
# Output: Insurance compliance score: 1.00
```

Or use the CLI (after installing the package):

```bash
litev --demo
```

## 📖 API Reference

### Core Classes

#### `Config`
Configuration for the audit process.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `chunk_size` | `int` | `1024` | Maximum characters per chunk. |
| `chunk_overlap` | `int` | `200` | Overlap between consecutive chunks. |
| `log_file` | `Path` | `"results.jsonl"` | Path for JSONL audit logs. |
| `model_provider` | `str` | `"stub"` | Provider name (`"stub"`, `"bedrock"`, etc.). |
| `model_name` | `str` | `"gpt‑4o‑mini"` | Model identifier (provider‑specific). |

#### `Data`
The document to be audited.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | *(required)* | The raw text content. |
| `metadata` | `Dict[str, Any]` | `{}` | Optional metadata for logging. |

#### `Rubric`
The rule‑set (ground truth) for evaluation.

| Field | Type | Description |
|-------|------|-------------|
| `text` | `str` | Plain‑text rubric describing the required criteria. |

#### `Chunk`
A piece of the original document.

| Field | Type | Description |
|-------|------|-------------|
| `index` | `int` | Zero‑based chunk index. |
| `text` | `str` | The chunk’s text content. |
| `passed` | `Optional[bool]` | Audit result (`True`/`False`/`None`). |
| `raw_resp` | `Optional[str]` | Raw response from the model provider. |

### Abstract Base Class

#### `ScoreStrategy`
Subclass this to implement custom scoring logic.

```python
class ScoreStrategy(ABC):
    @abstractmethod
    def compute(self, chunks: List[Chunk]) -> float:
        """Return a score in [0.0, 1.0] based on the audit results."""
```

**Built‑in strategies:**
- `PassRateStrategy` – Simple fraction of passing chunks.

### Functions

#### `chunk_document(data: Data, config: Config) → List[Chunk]`
Splits the document into overlapping chunks according to the configuration.

#### `audit_chunk(chunk: Chunk, rubric: Rubric, config: Config) → None`
Evaluates a single chunk against the rubric. **Override this function to integrate with a real model provider.** The default stub always marks chunks as passed.

#### `run_audit(data: Data, rubric: Rubric, config: Config, score_strategy: ScoreStrategy) → float`
Orchestrates the entire audit: chunking, evaluating each chunk, and computing the final score.

## ⚙️ Configuration & Extension

### Integrating a Real Model Provider

To replace the stub with an actual LLM (e.g., OpenAI, Anthropic, Bedrock):

1. Subclass or monkey‑patch `audit_chunk` to call your provider’s API.
2. Format the chunk text and rubric into a prompt.
3. Parse the model’s response into a Boolean `passed` value.
4. Store any raw response in `chunk.raw_resp`.

Example skeleton:

```python
async def audit_chunk_openai(chunk: Chunk, rubric: Rubric, config: Config) -> None:
    prompt = f"""
    Rubric:
    {rubric.text}

    Document chunk:
    {chunk.text}

    Does this chunk satisfy the rubric? Answer only "YES" or "NO".
    """
    # Call OpenAI API
    response = await openai.chat.completions.create(...)
    answer = response.choices[0].message.content.strip().upper()
    chunk.passed = answer == "YES"
    chunk.raw_resp = response
```

### Custom Scoring Strategies

Implement the `ScoreStrategy` abstract class to tailor scoring to your use case. Examples:

- **Weighted keywords** (as shown in the quick‑start)
- **Threshold‑based scoring** (require a minimum number of passing chunks)
- **Position‑aware scoring** (weight chunks differently based on their location)
- **Multi‑criteria scoring** (different rubrics for different sections)

### Adjusting Chunking

The default chunking algorithm splits text with a sliding window of size `chunk_size` and step `chunk_size - chunk_overlap`. If you need more sophisticated chunking (e.g., by sentences, paragraphs, or semantic boundaries), replace `chunk_document` with your own implementation.

## 📋 Example Workflow

1. **Define your rubric** – Write clear, plain‑text rules that a human (or model) can evaluate.
2. **Prepare your document** – Load the text into a `Data` object, optionally adding metadata.
3. **Choose/implement a model provider** – Start with the stub, then integrate a real LLM.
4. **Select a scoring strategy** – Use `PassRateStrategy` for simple pass/fail, or create a custom strategy.
5. **Run the audit** – Call `run_audit` with your configuration.
6. **Interpret the score** – A score of 1.0 means all criteria are satisfied; 0.0 means none are.

## 🧪 Testing

Run the included insurance example:

```bash
uv run examples/insurance.py
```

To test your own integrations, create a new script in the `examples/` directory and follow the same pattern.

## 🔮 Roadmap

Planned enhancements:

- [ ] Built‑in integrations for popular LLM providers (OpenAI, Anthropic, Bedrock, etc.)
- [ ] Support for multi‑modal rubrics (regex patterns, numeric thresholds, etc.)
- [ ] Batch processing and parallel auditing
- [ ] Web UI and/or CLI for interactive audits
- [ ] Pre‑built scoring strategies for common regulatory frameworks

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License

LiteV is released under the [MIT License](LICENSE).

---

**LiteV** – Lightweight, versatile, and focused on vetting/auditing tasks.