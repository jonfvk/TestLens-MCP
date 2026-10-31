import pytest

from testlens.output import classify_failure


@pytest.mark.parametrize(
    "failure, category",
    [
        ({"kind": "error", "message": "request timed out"}, "timeout"),
        ({"kind": "error", "traceback": "ModuleNotFoundError: no module named x"}, "import"),
        ({"kind": "error", "message": "connection refused"}, "network"),
        ({"kind": "error", "message": "permission denied"}, "environment"),
        ({"kind": "failure", "message": "expected 2 got 1"}, "assertion"),
        ({"kind": "error", "message": "unexpected exception"}, "runtime"),
    ],
)
def test_classifies_failures_from_explicit_evidence(failure, category):
    assert classify_failure(failure) == category
