"""Parser for JUnit and pytest JUnit XML reports."""
from pathlib import Path
import math
import xml.etree.ElementTree as ET

from testlens.models import TestFailure, TestReport, TestSuite


class ReportFormatError(ValueError):
    """Raised when an XML file is not a supported test report."""


def _count(element: ET.Element, attribute: str, fallback: int) -> int:
    value = element.get(attribute)
    if value is None:
        return fallback
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ReportFormatError(f"Invalid {attribute} count in suite") from exc
    if parsed < 0:
        raise ReportFormatError(f"Negative {attribute} count in suite")
    return parsed


def _duration(element: ET.Element) -> float:
    value = element.get("time", "0")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ReportFormatError("Invalid suite duration") from exc
    if not math.isfinite(parsed) or parsed < 0:
        raise ReportFormatError("Suite duration must be a finite non-negative number")
    return parsed


def parse_report(path: Path) -> TestReport:
    """Parse a JUnit ``testsuite`` or ``testsuites`` XML document."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ReportFormatError(f"Invalid XML report: {exc}") from exc

    if root.tag == "testsuite":
        suite_elements = [root]
    elif root.tag == "testsuites":
        suite_elements = list(root.findall("testsuite"))
    else:
        raise ReportFormatError("Expected a testsuite or testsuites XML root")

    if not suite_elements:
        raise ReportFormatError("Report contains no test suites")

    suites = []
    failures = []
    for suite_element in suite_elements:
        cases = list(suite_element.findall("testcase"))
        failure_nodes = [
            (case, node)
            for case in cases
            for node in (case.find("failure"), case.find("error"))
            if node is not None
        ]
        skipped_nodes = [case for case in cases if case.find("skipped") is not None]
        suite_name = suite_element.get("name", "unnamed")
        suites.append(
            TestSuite(
                name=suite_name,
                tests=_count(suite_element, "tests", len(cases)),
                failures=_count(
                    suite_element,
                    "failures",
                    sum(node.tag == "failure" for _, node in failure_nodes),
                ),
                errors=_count(
                    suite_element,
                    "errors",
                    sum(node.tag == "error" for _, node in failure_nodes),
                ),
                skipped=_count(suite_element, "skipped", len(skipped_nodes)),
                duration_seconds=_duration(suite_element),
            )
        )
        for case, node in failure_nodes:
            failures.append(
                TestFailure(
                    suite=suite_name,
                    classname=case.get("classname", ""),
                    name=case.get("name", "unnamed"),
                    kind=node.tag,
                    message=node.get("message", ""),
                    traceback=(node.text or "").strip(),
                    duration_seconds=_duration(case),
                )
            )

    return TestReport(path=path, suites=tuple(suites), failures=tuple(failures))
