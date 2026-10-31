"""Command-line entry point for TestLens."""
import argparse


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="testlens",
        description="Inspect JUnit test reports without modifying the workspace.",
    )
    parser.add_argument("--version", action="version", version="testlens 0.1.0")
    return parser


def main(argv: list[str] | None = None) -> int:
    create_parser().parse_args(argv)
    return 0
