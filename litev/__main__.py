#!/usr/bin/env python3
"""Command-line entry point for LiteV."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

from . import (
    Config,
    Data,
    Rubric,
    PassRateStrategy,
    chunk_document,
    audit_chunk,
    run_audit,
)


def demo() -> None:
    """Run the built-in insurance example."""
    import importlib.util
    example_path = Path(__file__).parent.parent / "examples" / "insurance.py"
    spec = importlib.util.spec_from_file_location("insurance", example_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    asyncio.run(module.main())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LiteV: Lightweight vetting/auditing system"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the insurance policy compliance demo",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()