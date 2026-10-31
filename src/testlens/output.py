"""Stable serialization for CLI and MCP responses."""
from dataclasses import asdict
from typing import Any

from testlens.models import TestReport


def classify_failure(failure: dict[str, Any]) -> str:
    """Assign a transparent heuristic category to a test failure."""
    text = " ".join(
        str(failure.get(field, ""))
        for field in ("kind", "message", "traceback")
    ).lower()
    if "timeout" in text or "timed out" in text:
        return "timeout"
    if "modulenotfounderror" in text or "importerror" in text or "no module named" in text:
        return "import"
    if any(term in text for term in ("connection refused", "connectionerror", "dns", "network")):
        return "network"
    if any(term in text for term in ("permission denied", "file not found", "missing config")):
        return "environment"
    if failure.get("kind") == "failure":
        return "assertion"
    return "runtime"


def report_to_dict(report: TestReport) -> dict[str, Any]:
    failure_details = []
    for failure in report.failures:
        detail = asdict(failure)
        detail["category"] = classify_failure(detail)
        failure_details.append(detail)
    return {
        "path": report.path.as_posix(),
        "tests": report.tests,
        "passed": report.passed,
        "failures": report.failures_count,
        "errors": report.errors_count,
        "skipped": report.skipped_count,
        "duration_seconds": report.duration_seconds,
        "suites": [asdict(suite) for suite in report.suites],
        "failure_details": failure_details,
    }
