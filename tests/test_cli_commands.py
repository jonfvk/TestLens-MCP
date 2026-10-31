import json
from pathlib import Path

from testlens.cli import main


def _report(workspace: Path):
    (workspace / "junit.xml").write_text(
        """<testsuite name="unit" tests="2" failures="1" errors="0" skipped="0" time="0.2">
  <testcase classname="sample.Tests" name="test_ok" />
  <testcase classname="sample.Tests" name="test_bad">
    <failure message="expected">assert False</failure>
  </testcase>
</testsuite>"""
    )


def test_cli_lists_reports(tmp_path, capsys):
    _report(tmp_path)

    assert main(["--workspace", str(tmp_path), "list"]) == 0
    assert capsys.readouterr().out.strip() == "junit.xml"


def test_cli_summary_json(tmp_path, capsys):
    _report(tmp_path)

    assert main(["--workspace", str(tmp_path), "--json", "summary", "junit.xml"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["tests"] == 2
    assert result["failures"] == 1


def test_cli_failures_and_unsafe_path(tmp_path, capsys):
    _report(tmp_path)
    assert main(["--workspace", str(tmp_path), "failures", "junit.xml"]) == 0
    assert "test_bad" in capsys.readouterr().out

    assert main(["--workspace", str(tmp_path), "summary", "../outside.xml"]) == 2
    assert "cannot traverse" in capsys.readouterr().err
