"""Immutable result types for parsed test reports."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestFailure:
    suite: str
    classname: str
    name: str
    kind: str
    message: str
    traceback: str
    duration_seconds: float


@dataclass(frozen=True)
class TestSuite:
    name: str
    tests: int
    failures: int
    errors: int
    skipped: int
    duration_seconds: float


@dataclass(frozen=True)
class TestReport:
    path: Path
    suites: tuple[TestSuite, ...]
    failures: tuple[TestFailure, ...]

    @property
    def tests(self) -> int:
        return sum(suite.tests for suite in self.suites)

    @property
    def failures_count(self) -> int:
        return sum(suite.failures for suite in self.suites)

    @property
    def errors_count(self) -> int:
        return sum(suite.errors for suite in self.suites)

    @property
    def skipped_count(self) -> int:
        return sum(suite.skipped for suite in self.suites)

    @property
    def passed(self) -> int:
        return max(0, self.tests - self.failures_count - self.errors_count - self.skipped_count)

    @property
    def duration_seconds(self) -> float:
        return sum(suite.duration_seconds for suite in self.suites)
