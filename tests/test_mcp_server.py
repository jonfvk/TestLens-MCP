import asyncio
import json
import os
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
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


def test_stdio_server_protocol_round_trip(tmp_path: Path):
    async def verify_protocol():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "testlens", "--workspace", str(tmp_path), "serve"],
            env=os.environ.copy(),
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                return {tool.name for tool in tools.tools}

    tools = asyncio.run(verify_protocol())

    assert "list_test_reports" in tools
    assert "summarize_test_report" in tools
    assert "get_test_failures" in tools
