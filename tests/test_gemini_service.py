"""Tests for app.services.gemini_service."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import Settings
from app.services.gemini_service import GeminiService, GeminiServiceError


# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture()
def settings() -> Settings:
    """Return a dummy Settings instance (no real key required)."""
    return Settings(
        gemini_api_key="AIzaSy-test-key-0000",
        gemini_model="gemini-2.0-flash",
        temperature=0.2,
    )


@pytest.fixture()
def mock_gemini_response() -> SimpleNamespace:
    """Return a fake Gemini generate_content-style response."""
    return SimpleNamespace(text="Paris is the capital of France.")


# ──────────────────────────────────────────────────────────────────────
# Tests – initialisation
# ──────────────────────────────────────────────────────────────────────


class TestGeminiServiceInit:
    """Verify service initialisation."""

    @patch("app.services.gemini_service.genai")
    def test_creates_client(self, mock_genai: MagicMock, settings: Settings) -> None:
        """The Gemini client is instantiated with the configured key."""
        service = GeminiService(settings)
        mock_genai.Client.assert_called_once_with(api_key=settings.gemini_api_key)
        assert service is not None


# ──────────────────────────────────────────────────────────────────────
# Tests – get_answer
# ──────────────────────────────────────────────────────────────────────


class TestGetAnswer:
    """Verify the get_answer method."""

    @patch("app.services.gemini_service.genai")
    def test_returns_content(
        self,
        mock_genai: MagicMock,
        settings: Settings,
        mock_gemini_response: SimpleNamespace,
    ) -> None:
        """A successful API response is returned as a plain string."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        messages = [
            {"role": "user", "content": "What is the capital of France?"},
        ]
        result = service.get_answer(messages)
        assert result == "Paris is the capital of France."
        mock_client.models.generate_content.assert_called_once()

    @patch("app.services.gemini_service.genai")
    def test_passes_model(
        self,
        mock_genai: MagicMock,
        settings: Settings,
        mock_gemini_response: SimpleNamespace,
    ) -> None:
        """Model from settings is forwarded to the API."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        service.get_answer([{"role": "user", "content": "Hi"}])

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == settings.gemini_model

    @patch("app.services.gemini_service.genai")
    def test_handles_none_text(
        self,
        mock_genai: MagicMock,
        settings: Settings,
    ) -> None:
        """A response with ``text=None`` returns an empty string."""
        response = SimpleNamespace(text=None)
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        assert service.get_answer([{"role": "user", "content": "Hi"}]) == ""

    @patch("app.services.gemini_service.genai")
    def test_maps_assistant_role_to_model(
        self,
        mock_genai: MagicMock,
        settings: Settings,
        mock_gemini_response: SimpleNamespace,
    ) -> None:
        """The 'assistant' role is mapped to 'model' for Gemini."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "Follow-up"},
        ]
        service.get_answer(messages)

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        contents = call_kwargs["contents"]
        assert contents[0].role == "user"
        assert contents[1].role == "model"
        assert contents[2].role == "user"

    @patch("app.services.gemini_service.genai")
    def test_skips_system_messages(
        self,
        mock_genai: MagicMock,
        settings: Settings,
        mock_gemini_response: SimpleNamespace,
    ) -> None:
        """System messages are filtered out (handled via system_instruction)."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_gemini_response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
        service.get_answer(messages)

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        contents = call_kwargs["contents"]
        assert len(contents) == 1
        assert contents[0].role == "user"


# ──────────────────────────────────────────────────────────────────────
# Tests – error handling
# ──────────────────────────────────────────────────────────────────────


class TestGetAnswerErrors:
    """Verify that API errors are wrapped in GeminiServiceError."""

    @patch("app.services.gemini_service.genai")
    def test_authentication_error(self, mock_genai: MagicMock, settings: Settings) -> None:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API key not valid. Please pass a valid API key.")
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        with pytest.raises(GeminiServiceError, match="Authentication failed"):
            service.get_answer([{"role": "user", "content": "Hi"}])

    @patch("app.services.gemini_service.genai")
    def test_rate_limit_error(self, mock_genai: MagicMock, settings: Settings) -> None:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("Resource exhausted: quota exceeded")
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        with pytest.raises(GeminiServiceError, match="Rate limit or quota exceeded"):
            service.get_answer([{"role": "user", "content": "Hi"}])

    @patch("app.services.gemini_service.genai")
    def test_connection_error(self, mock_genai: MagicMock, settings: Settings) -> None:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("Connection timeout")
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        with pytest.raises(GeminiServiceError, match="Unable to reach"):
            service.get_answer([{"role": "user", "content": "Hi"}])

    @patch("app.services.gemini_service.genai")
    def test_unexpected_error(self, mock_genai: MagicMock, settings: Settings) -> None:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("boom")
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        with pytest.raises(GeminiServiceError, match="unexpected error"):
            service.get_answer([{"role": "user", "content": "Hi"}])

    @patch("app.services.gemini_service.genai")
    def test_missing_text_attribute(self, mock_genai: MagicMock, settings: Settings) -> None:
        """A response without a .text attribute triggers a GeminiServiceError."""
        response = MagicMock(spec=[])  # no attributes at all
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = response
        mock_genai.Client.return_value = mock_client

        service = GeminiService(settings)
        with pytest.raises(GeminiServiceError, match="unexpected response format"):
            service.get_answer([{"role": "user", "content": "Hi"}])
