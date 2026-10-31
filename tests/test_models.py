from pathlib import Path

from testlens.models import TestReport, TestSuite


def test_report_aggregates_suite_counts():
    report = TestReport(
        Path("junit.xml"),
        (
            TestSuite("unit", 10, 1, 1, 2, 1.5),
            TestSuite("integration", 5, 0, 0, 1, 2.0),
        ),
        (),
    )

    assert report.tests == 15
    assert report.failures_count == 1
    assert report.errors_count == 1
    assert report.skipped_count == 3
    assert report.passed == 10
    assert report.duration_seconds == 3.5


def test_empty_report_has_zero_totals():
    report = TestReport(Path("empty.xml"), (), ())

    assert report.tests == 0
    assert report.passed == 0
    assert report.duration_seconds == 0
