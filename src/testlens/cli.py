"""Command-line entry point for TestLens."""
import argparse
import json
import sys
from pathlib import Path

from testlens.catalog import ReportCatalog
from testlens.output import report_to_dict
from testlens.parser import parse_report


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="testlens",
        description="Inspect JUnit test reports without modifying the workspace.",
    )
    parser.add_argument("--version", action="version", version="testlens 0.1.0")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace root for report discovery (default: current directory)",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List XML reports beneath the workspace")
    for command, help_text in (
        ("summary", "Summarize a JUnit report"),
        ("failures", "Show failing test details"),
    ):
        subcommand = commands.add_parser(command, help=help_text)
        subcommand.add_argument("report", help="Workspace-relative XML report path")
    commands.add_parser("serve", help="Run the read-only MCP server over stdio")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit machine-readable JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    if args.command == "serve":
        from testlens.mcp_server import create_server

        create_server(args.workspace).run("stdio")
        return 0
    try:
        catalog = ReportCatalog(args.workspace)
        if args.command == "list":
            result = catalog.list_reports()
        else:
            path = catalog.resolve_report(args.report)
            report = parse_report(path)
            result = report_to_dict(report)
            result["path"] = Path(args.report).as_posix()
            if args.command == "failures":
                result = {
                    "path": result["path"],
                    "failure_details": result["failure_details"],
                }
    except (OSError, ValueError) as exc:
        print(f"testlens: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(result, indent=2))
    elif args.command == "list":
        print("\n".join(result) if result else "No XML reports found.")
    elif args.command == "failures":
        failures = result["failure_details"]
        if not failures:
            print("No failing tests.")
        for failure in failures:
            print(f"{failure['suite']} :: {failure['classname']}::{failure['name']}")
            print(f"{failure['kind']}: {failure['message']}")
            if failure["traceback"]:
                print(failure["traceback"])
    else:
        print(
            f"{result['path']}: {result['tests']} tests, {result['passed']} passed, "
            f"{result['failures']} failed, {result['errors']} errors, "
            f"{result['skipped']} skipped ({result['duration_seconds']:.3f}s)"
        )
    return 0
