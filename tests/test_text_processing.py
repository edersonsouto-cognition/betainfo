"""Tests for the text_processing module."""

from __future__ import annotations

from src.utils.text_processing import (
    analyze_text,
    count_characters,
    count_words,
    extract_emails,
    extract_hashtags,
    slugify,
)


class TestCountWords:
    def test_basic(self) -> None:
        result = count_words("hello world hello")
        assert result["hello"] == 2
        assert result["world"] == 1

    def test_empty(self) -> None:
        assert count_words("") == {}


class TestCountCharacters:
    def test_skips_whitespace(self) -> None:
        result = count_characters("a b c")
        assert " " not in result
        assert result["a"] == 1


class TestExtractEmails:
    def test_finds_emails(self) -> None:
        text = "Contact alice@example.com or bob@example.org"
        emails = extract_emails(text)
        assert "alice@example.com" in emails
        assert len(emails) == 2


class TestExtractHashtags:
    def test_finds_hashtags(self) -> None:
        text = "Working on #devin and #python today"
        tags = extract_hashtags(text)
        assert "devin" in tags
        assert "python" in tags


class TestSlugify:
    def test_basic_slugify(self) -> None:
        assert slugify("Hello World!") == "hello-world"

    def test_collapses_spaces(self) -> None:
        assert slugify("  too   many   spaces  ") == "too-many-spaces"


class TestAnalyzeText:
    def test_returns_expected_keys(self) -> None:
        result = analyze_text("Hello world. This is a test.")
        assert "word_count" in result
        assert "sentence_count" in result
        assert result["word_count"] == 6
        assert result["sentence_count"] == 2
