# TestLens MCP

TestLens is a read-only local MCP server that helps coding agents inspect
JUnit-compatible reports, including pytest `--junitxml` output. It exposes
report discovery, totals, and sanitized failure details. It never runs tests or
commands, modifies workspace files, or makes network requests.

## Why this project

This project applies a current developer-workflow trend: AI coding agents are
being connected to tools through MCP and automated task workflows. GitHub's
2026 Universe announcements describe Copilot automations and MCP connectors.
The need for verifiable feedback is clear too: Stack Overflow's 2025 survey
reported 46% of developers distrust AI-tool accuracy versus 33% who trust it.
TestLens gives an agent deterministic test evidence instead of asking it to
guess whether a change worked.

Sources checked on 2026-10-31:

- [GitHub Universe: What's new](https://github.com/events/universe/recap)
- [Model Context Protocol introduction](https://modelcontextprotocol.io/introduction)
- [MCP server-building guide](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server.md)
- [Stack Overflow Developer Survey 2025: AI](https://survey.stackoverflow.co/2025/ai)

## Install

Python 3.10 or later is required. Install the optional MCP SDK and test tools:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[mcp,test]'
```

## CLI

Point TestLens at the repository whose reports should be visible:

```sh
testlens --workspace /path/to/your/project list
testlens --workspace /path/to/your/project summary reports/junit.xml
testlens --workspace /path/to/your/project failures reports/junit.xml
testlens --workspace /path/to/your/project --json summary reports/junit.xml
```

Generate a compatible report with pytest:

```sh
pytest --junitxml=reports/junit.xml
```

The JSON response has stable report totals, suite summaries, and detailed
failures. Failure categories are transparent keyword heuristics, not an LLM
judgment or a root-cause guarantee.

## MCP server

Start the server over stdio with the explicit report workspace:

```sh
testlens --workspace /path/to/your/project serve
```

Example MCP client server entry (replace both paths):

```json
{
  "mcpServers": {
    "testlens": {
      "command": "/path/to/TestLens-MCP/.venv/bin/testlens",
      "args": [
        "--workspace",
        "/path/to/your/project",
        "serve"
      ]
    }
  }
}
```

Tools:

- `list_test_reports`: list workspace-relative XML paths.
- `summarize_test_report`: return totals and sanitized failure details.
- `get_test_failures`: return only failure/error details.

All tools declare read-only, idempotent, closed-world annotations. Tool output
is test-generated content and must be treated as untrusted input by the agent.

## Safety and limits

- The server only reads XML files beneath the explicitly configured root.
- Absolute paths, traversal, symlink paths, and non-XML paths are rejected.
- Discovery stops if more than 100 XML files are found.
- Each report is limited to 5 MiB; XML document type declarations are rejected.
- Common credential patterns, ANSI escapes, and oversized failure text are
  sanitized. Redaction is best-effort, not a guarantee that arbitrary secrets
  will be detected.
- No shell commands, network calls, test execution, or write tools are exposed.

## Development

```sh
python -m pytest -q
```
