"""Stable serialization for CLI and MCP responses."""
from dataclasses import asdict
from typing import Any

from testlens.models import TestReport


def report_to_dict(report: TestReport) -> dict[str, Any]:
    return {
        "path": report.path.as_posix(),
        "tests": report.tests,
        "passed": report.passed,
        "failures": report.failures_count,
        "errors": report.errors_count,
        "skipped": report.skipped_count,
        "duration_seconds": report.duration_seconds,
        "suites": [asdict(suite) for suite in report.suites],
        "failure_details": [asdict(failure) for failure in report.failures],
    }
