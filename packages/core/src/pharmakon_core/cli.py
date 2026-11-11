"""The `pharmakon` command-line tool."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from pharmakon_core import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pharmakon",
        description="Look up drug and molecule data from the command line.",
    )
    parser.add_argument("--version", action="version", version=f"pharmakon {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    build_parser().parse_args(argv)
    return 0
