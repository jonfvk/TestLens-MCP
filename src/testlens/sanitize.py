"""Basic secret and terminal-control sanitization for report text."""
import re


_ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")
_REDACTIONS = (
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*", re.IGNORECASE), "Bearer [REDACTED]"),
    (re.compile(r"\b(?:sk|gh[pousr])[-_][A-Za-z0-9_-]{16,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED_AWS_KEY]"),
    (
        re.compile(
            r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)"
            r"(\s*[:=]\s*)(['\"]?)[^\s,;'\"]{4,}\3",
            re.IGNORECASE,
        ),
        r"\1\2[REDACTED]",
    ),
)


def sanitize_text(value: str, *, max_chars: int = 8000) -> str:
    """Redact common credential patterns, ANSI escapes, and oversized text."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    text = _ANSI_ESCAPE.sub("", value)
    for pattern, replacement in _REDACTIONS:
        text = pattern.sub(replacement, text)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[truncated]"
    return text
