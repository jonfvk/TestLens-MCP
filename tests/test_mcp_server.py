import asyncio
import json
from pathlib import Path

from testlens.mcp_server import create_server


def test_server_exposes_read_only_report_tools(tmp_path: Path):
    (tmp_path / "junit.xml").write_text(
        """<testsuite name="unit" tests="1" failures="1">
  <testcase classname="sample.Tests" name="test_bad">
    <failure message="password=hunter2">assert False</failure>
  </testcase>
</testsuite>"""
    )
    server = create_server(tmp_path)

    tools = asyncio.run(server.list_tools())

    assert {tool.name for tool in tools} == {
        "list_test_reports",
        "summarize_test_report",
        "get_test_failures",
    }
    assert all(tool.annotations.read_only_hint for tool in tools)
    assert all(tool.annotations.open_world_hint is False for tool in tools)


def test_server_tool_calls_return_sanitized_data(tmp_path: Path):
    (tmp_path / "junit.xml").write_text(
        """<testsuite name="unit" tests="1" failures="1">
  <testcase classname="sample.Tests" name="test_bad">
    <failure message="password=hunter2">assert False</failure>
  </testcase>
</testsuite>"""
    )
    server = create_server(tmp_path)

    result = asyncio.run(server.call_tool("summarize_test_report", {"report_path": "junit.xml"}))

    assert result.is_error is False
    response = json.loads(result.content[0].text)
    assert response["tests"] == 1
    assert "hunter2" not in result.content[0].text
