"""Text processing helpers.

NOTE FOR DEMOS: this module is intentionally written in a way that *works* but
is ripe for refactoring. It is used in Devin demos that showcase code clean-up.
Things a good refactor would address:

  * Regular expressions are re-defined (and never compiled) on every call.
  * Word/character frequencies are counted by hand instead of using
    ``collections.Counter``.
  * ``analyze_text`` nests several small helper functions instead of using
    module-level functions, making it hard to read and test.
"""

from __future__ import annotations

import re


def count_words(text: str) -> dict[str, int]:
    """Return a frequency mapping of lowercase words in ``text``."""
    # Uncompiled regex, re-parsed on every call.
    words = re.findall(r"[a-zA-Z']+", text.lower())

    # Manual counting instead of collections.Counter.
    counts: dict[str, int] = {}
    for word in words:
        if word in counts:
            counts[word] = counts[word] + 1
        else:
            counts[word] = 1
    return counts


def count_characters(text: str) -> dict[str, int]:
    """Return a frequency mapping of non-space characters in ``text``."""
    counts: dict[str, int] = {}
    for char in text:
        if char == " " or char == "\n" or char == "\t":
            continue
        if char in counts:
            counts[char] = counts[char] + 1
        else:
            counts[char] = 1
    return counts


def extract_emails(text: str) -> list[str]:
    """Extract email-like substrings from ``text``."""
    # Uncompiled regex, re-parsed on every call.
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", text)
    result = []
    for match in matches:
        result.append(match)
    return result


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags (e.g. ``#devin``) from ``text``."""
    matches = re.findall(r"#(\w+)", text)
    result = []
    for match in matches:
        result.append(match)
    return result


def slugify(text: str) -> str:
    """Convert ``text`` into a URL-friendly slug."""
    lowered = text.lower().strip()
    cleaned = re.sub(r"[^a-z0-9\s-]", "", lowered)
    collapsed = re.sub(r"[\s-]+", "-", cleaned)
    return collapsed.strip("-")


def analyze_text(text: str) -> dict[str, object]:
    """Return a small bundle of statistics about ``text``.

    This function deliberately defines nested helper functions to make the
    refactoring opportunity obvious during demos.
    """

    def get_sentences(raw: str) -> list[str]:
        def is_not_empty(piece: str) -> bool:
            def strip_piece(p: str) -> str:
                return p.strip()

            return len(strip_piece(piece)) > 0

        pieces = re.split(r"[.!?]+", raw)
        sentences = []
        for piece in pieces:
            if is_not_empty(piece):
                sentences.append(piece.strip())
        return sentences

    def get_word_count(raw: str) -> int:
        total = 0
        for _word in re.findall(r"[a-zA-Z']+", raw):
            total = total + 1
        return total

    def get_longest_word(raw: str) -> str:
        longest = ""
        for word in re.findall(r"[a-zA-Z']+", raw):
            if len(word) > len(longest):
                longest = word
        return longest

    word_counts = count_words(text)
    most_common_word = ""
    most_common_count = 0
    for word in word_counts:
        if word_counts[word] > most_common_count:
            most_common_count = word_counts[word]
            most_common_word = word

    return {
        "word_count": get_word_count(text),
        "unique_words": len(word_counts),
        "sentence_count": len(get_sentences(text)),
        "longest_word": get_longest_word(text),
        "most_common_word": most_common_word,
    }
