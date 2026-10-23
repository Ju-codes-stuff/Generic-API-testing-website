"""Google Gemini API service layer.

Encapsulates all communication with the Google Gemini API so that
the Streamlit UI never calls the API directly.
"""

from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class GeminiServiceError(Exception):
    """A user-safe error raised when the Gemini API call fails.

    The message intentionally omits credentials and internal details.
    """


class GeminiService:
    """Thin wrapper around the Google Gemini API.

    Args:
        settings: Validated application settings.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(api_key=settings.gemini_api_key)
        logger.info(
            "GeminiService initialised (model=%s, temperature=%s)",
            settings.gemini_model,
            settings.temperature,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_answer(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """Send *messages* to the Gemini API and return the model's reply.

        Args:
            messages: A list of message dicts with ``role`` and ``content``
                keys. Roles should be ``"user"`` or ``"assistant"``.
                The system prompt is handled internally.

        Returns:
            The text content of the model's response.

        Raises:
            GeminiServiceError: On any API or network failure, with a
                user-friendly message that never leaks credentials.
        """

        try:
            # Convert conversation history to Gemini Content objects.
            contents = self._build_contents(messages)

            response = self._client.models.generate_content(
                model=self._settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=self._settings.temperature,
                ),
            )
            answer = self._extract_text(response)
            logger.info(
                "Received response from Gemini (model=%s)",
                self._settings.gemini_model,
            )
            return answer

        except GeminiServiceError:
            # Re-raise our own errors as-is.
            raise

        except Exception as exc:
            error_msg = str(exc).lower()

            if "api key" in error_msg or "permission" in error_msg or "401" in error_msg or "403" in error_msg:
                logger.error("Gemini authentication failed – check your API key.")
                raise GeminiServiceError(
                    "Authentication failed. Please verify that your Gemini API key "
                    "is correct and has not expired."
                ) from exc

            if "quota" in error_msg or "rate" in error_msg or "429" in error_msg or "resource exhausted" in error_msg:
                logger.error("Gemini rate limit / quota exceeded.")
                raise GeminiServiceError(
                    "Rate limit or quota exceeded. Please wait a moment and try again, "
                    "or check your Google AI Studio usage."
                ) from exc

            if "connect" in error_msg or "network" in error_msg or "timeout" in error_msg:
                logger.error("Could not connect to the Gemini API.")
                raise GeminiServiceError(
                    "Unable to reach the Gemini API. Please check your network "
                    "connection and try again."
                ) from exc

            # Generic catch-all – log the real error, surface a safe message.
            logger.exception("Unexpected error while calling Gemini API.")
            raise GeminiServiceError(
                "An unexpected error occurred while generating the answer. "
                "Please try again later."
            ) from exc

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _build_contents(
        messages: list[dict[str, str]],
    ) -> list[types.Content]:
        """Convert chat messages to Gemini ``Content`` objects.

        Gemini uses ``"user"`` and ``"model"`` roles (not ``"assistant"``).
        System messages are excluded here – they are passed via
        ``system_instruction`` in the config.
        """

        contents: list[types.Content] = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                # System prompt is handled via system_instruction.
                continue
            # Map "assistant" → "model" for Gemini.
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part(text=msg["content"])],
                )
            )
        return contents

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Extract the text content from a Gemini generate_content response."""

        try:
            text = response.text
            if text is None:
                return ""
            return text.strip()
        except (AttributeError, ValueError) as exc:
            logger.error("Failed to extract text from Gemini response: %s", exc)
            raise GeminiServiceError(
                "Received an unexpected response format from the API."
            ) from exc
