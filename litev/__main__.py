#!/usr/bin/env python3
"""Command-line entry point for LiteV."""

import argparse
import sys

from . import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LiteV: Lightweight vetting/auditing system"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    # Currently no subcommands; print help and exit.
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()