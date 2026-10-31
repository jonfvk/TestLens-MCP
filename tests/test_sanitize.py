import pytest

from testlens.sanitize import sanitize_text


def test_sanitize_removes_common_credentials_and_ansi():
    text = (
        "\x1b[31mfailed\x1b[0m "
        "Bearer abc.def "
        "sk-12345678901234567890 "
        "ghp_12345678901234567890 "
        "AKIA1234567890ABCDEF "
        "password=hunter2"
    )

    sanitized = sanitize_text(text)

    assert "\x1b" not in sanitized
    assert "abc.def" not in sanitized
    assert "sk-12345678901234567890" not in sanitized
    assert "ghp_12345678901234567890" not in sanitized
    assert "AKIA1234567890ABCDEF" not in sanitized
    assert "hunter2" not in sanitized
    assert "[REDACTED]" in sanitized


def test_sanitize_limits_output_length():
    assert sanitize_text("abcdef", max_chars=3) == "abc\n[truncated]"


def test_sanitize_requires_positive_limit():
    with pytest.raises(ValueError, match="positive"):
        sanitize_text("text", max_chars=0)
