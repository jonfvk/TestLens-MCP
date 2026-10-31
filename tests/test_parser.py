from pathlib import Path

import pytest

from testlens.parser import ReportFormatError, parse_report


def test_parse_pytest_testsuites_report(tmp_path: Path):
    report_file = tmp_path / "junit.xml"
    report_file.write_text(
        """<?xml version="1.0"?>
<testsuites>
  <testsuite name="unit" tests="3" failures="1" errors="0" skipped="1" time="0.5">
    <testcase classname="sample.TestCalc" name="test_add" time="0.1" />
    <testcase classname="sample.TestCalc" name="test_subtract" time="0.2">
      <failure message="expected 2">assert 1 == 2</failure>
    </testcase>
    <testcase classname="sample.TestCalc" name="test_skip" time="0.0">
      <skipped message="not supported" />
    </testcase>
  </testsuite>
</testsuites>"""
    )

    report = parse_report(report_file)

    assert (report.tests, report.passed, report.failures_count, report.skipped_count) == (
        3,
        1,
        1,
        1,
    )
    assert report.failures[0].name == "test_subtract"
    assert report.failures[0].message == "expected 2"
    assert report.failures[0].traceback == "assert 1 == 2"


def test_parse_single_suite_and_error_node(tmp_path: Path):
    report_file = tmp_path / "junit.xml"
    report_file.write_text(
        """<testsuite name="integration">
  <testcase classname="api.TestClient" name="test_timeout">
    <error message="Timeout">request timed out</error>
  </testcase>
</testsuite>"""
    )

    report = parse_report(report_file)

    assert report.errors_count == 1
    assert report.failures[0].kind == "error"
    assert report.failures[0].suite == "integration"


@pytest.mark.parametrize(
    "xml, message",
    [
        ("<not-a-report />", "Expected"),
        ("<testsuites />", "no test suites"),
        ("<testsuite tests='bad' />", "Invalid tests"),
        ("<testsuite time='NaN'><testcase /></testsuite>", "finite"),
        ("<testsuite>", "Invalid XML"),
    ],
)
def test_reject_invalid_reports(tmp_path: Path, xml: str, message: str):
    report_file = tmp_path / "bad.xml"
    report_file.write_text(xml)

    with pytest.raises(ReportFormatError, match=message):
        parse_report(report_file)
