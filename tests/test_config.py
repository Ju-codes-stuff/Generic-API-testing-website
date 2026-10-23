"""Tests for app.config.settings."""

import os
from unittest.mock import patch

import pytest

from app.config.settings import ConfigurationError, Settings, load_settings


class TestLoadSettings:
    """Test suite for ``load_settings``."""

    @patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "AIzaSy-test-key-1234567890",
            "GEMINI_MODEL": "gemini-2.0-flash",
            "TEMPERATURE": "0.5",
        },
    )
    def test_loads_all_values(self) -> None:
        """All environment variables are loaded correctly."""
        settings = load_settings()
        assert settings.gemini_api_key == "AIzaSy-test-key-1234567890"
        assert settings.gemini_model == "gemini-2.0-flash"
        assert settings.temperature == 0.5

    @patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "AIzaSy-test-key-1234567890"},
        clear=False,
    )
    def test_uses_defaults_when_optional_vars_missing(self) -> None:
        """Defaults are applied for GEMINI_MODEL and TEMPERATURE."""
        env = os.environ.copy()
        env.pop("GEMINI_MODEL", None)
        env.pop("TEMPERATURE", None)
        with patch.dict(os.environ, env, clear=True):
            os.environ["GEMINI_API_KEY"] = "AIzaSy-test-key-1234567890"
            settings = load_settings()
            assert settings.gemini_model == "gemini-2.0-flash"
            assert settings.temperature == 0.2

    @patch.dict(os.environ, {}, clear=True)
    def test_raises_when_api_key_missing(self) -> None:
        """A clear error is raised when GEMINI_API_KEY is absent."""
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is not configured"):
            load_settings()

    @patch.dict(os.environ, {"GEMINI_API_KEY": "   "}, clear=True)
    def test_raises_when_api_key_blank(self) -> None:
        """A blank API key is treated as missing."""
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is not configured"):
            load_settings()

    @patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "your_gemini_api_key_here"},
        clear=True,
    )
    def test_raises_when_api_key_is_placeholder(self) -> None:
        """The placeholder value from .env.example is rejected."""
        with pytest.raises(ConfigurationError, match="GEMINI_API_KEY is not configured"):
            load_settings()

    @patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "AIzaSy-key", "TEMPERATURE": "not-a-number"},
        clear=True,
    )
    def test_raises_on_invalid_temperature(self) -> None:
        """A non-numeric TEMPERATURE triggers a clear error."""
        with pytest.raises(ConfigurationError, match="TEMPERATURE must be a valid number"):
            load_settings()

    @patch.dict(
        os.environ,
        {"GEMINI_API_KEY": "AIzaSy-key", "TEMPERATURE": "3.0"},
        clear=True,
    )
    def test_raises_on_out_of_range_temperature(self) -> None:
        """TEMPERATURE outside [0.0, 2.0] triggers a clear error."""
        with pytest.raises(ConfigurationError, match="TEMPERATURE must be between"):
            load_settings()


class TestSettingsImmutability:
    """Verify that Settings is truly frozen."""

    def test_frozen(self) -> None:
        settings = Settings(
            gemini_api_key="AIzaSy-key",
            gemini_model="gemini-2.0-flash",
            temperature=0.2,
        )
        with pytest.raises(AttributeError):
            settings.gemini_api_key = "changed"  # type: ignore[misc]