"""
Unit tests for preprocessor module
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

from preprocessor import clean_text, validate_text, detect_issues, calculate_metrics


class TestCleanText:
    """Tests for clean_text function"""

    def test_returns_string(self):
        assert isinstance(clean_text("hello"), str)

    def test_none_returns_empty(self):
        assert clean_text(None) == ""

    def test_empty_returns_empty(self):
        assert clean_text("") == ""

    def test_strips_whitespace(self):
        result = clean_text("  hello world  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_collapses_extra_spaces(self):
        result = clean_text("too   many    spaces")
        assert "  " not in result

    def test_content_preserved(self):
        text = "Victor ran away from the creature."
        result = clean_text(text)
        assert "Victor" in result
        assert "creature" in result


class TestValidateText:
    """Tests for validate_text function"""

    @pytest.fixture
    def cfg(self):
        return {
            "validation": {
                "min_words": 10,
                "max_words": 600,
                "min_chars": 50,
                "quality_threshold": 0.5
            },
            "issues": {
                "profanity_ratio_threshold": 0.30,
                "caps_threshold": 0.50,
                "punct_threshold": 0.10,
                "repetitive_chars": 4,
                "repetitive_words_threshold": 0.30
            }
        }

    @pytest.fixture
    def valid_text(self):
        return (
            "The creature opened its eyes and Victor ran away immediately. "
            "He could not handle what he had created with his own hands. "
            "The yellow eye fixated on him with great intensity and purpose."
        )

    def test_returns_dict(self, valid_text, cfg):
        result = validate_text(valid_text, cfg)
        assert isinstance(result, dict)

    def test_valid_text_passes(self, valid_text, cfg):
        result = validate_text(valid_text, cfg)
        assert result["is_valid"] is True

    def test_required_keys(self, valid_text, cfg):
        result = validate_text(valid_text, cfg)
        for key in ["is_valid", "quality_score", "word_count"]:
            assert key in result

    def test_empty_text_fails(self, cfg):
        result = validate_text("", cfg)
        assert result["is_valid"] is False


class TestCalculateMetrics:
    """Tests for calculate_metrics function"""

    def test_returns_dict(self):
        result = calculate_metrics("hello world test text here")
        assert isinstance(result, dict)

    def test_word_count_correct(self):
        result = calculate_metrics("one two three four five")
        assert result["word_count"] == 5

    def test_empty_text_zeros(self):
        result = calculate_metrics("")
        assert result["word_count"] == 0

    def test_none_returns_zeros(self):
        result = calculate_metrics(None)
        assert result["word_count"] == 0

    def test_required_keys(self):
        result = calculate_metrics("some sample text here today")
        for key in ["word_count", "char_count", "readability_score"]:
            assert key in result


class TestEdgeCases:
    """Edge case tests"""

    @pytest.fixture
    def cfg(self):
        return {
            "validation": {
                "min_words": 10,
                "max_words": 600,
                "min_chars": 50,
                "quality_threshold": 0.5
            },
            "issues": {
                "profanity_ratio_threshold": 0.30,
                "caps_threshold": 0.50,
                "punct_threshold": 0.10,
                "repetitive_chars": 4,
                "repetitive_words_threshold": 0.30
            }
        }

    def test_very_short_text(self, cfg):
        result = validate_text("Too short.", cfg)
        assert result["is_valid"] is False

    def test_unicode_characters(self):
        result = clean_text("Victor\u2019s creation was \u201camazing\u201d")
        assert "\u2019" not in result
        assert "\u201c" not in result