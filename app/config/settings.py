"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class ConfigurationError(Exception):
    """Raised when a required configuration value is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Immutable application settings.

    Attributes:
        gemini_api_key: The Google Gemini API key (never exposed in logs/UI).
        gemini_model: The Gemini model identifier to use.
        temperature: Sampling temperature for generation (0.0 – 2.0).
    """

    gemini_api_key: str
    gemini_model: str
    temperature: float


def load_settings() -> Settings:
    """Load and validate application settings from environment variables.

    Returns:
        A validated ``Settings`` instance.

    Raises:
        ConfigurationError: If ``GEMINI_API_KEY`` is missing or empty, or if
            ``TEMPERATURE`` cannot be parsed as a float.
    """

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ConfigurationError(
            "GEMINI_API_KEY is not configured. "
            "Please create a .env file with your Google Gemini API key. "
            "See .env.example for reference."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()

    raw_temperature = os.getenv("TEMPERATURE", "0.2").strip()
    try:
        temperature = float(raw_temperature)
    except ValueError as exc:
        raise ConfigurationError(
            f"TEMPERATURE must be a valid number, got '{raw_temperature}'."
        ) from exc

    if not 0.0 <= temperature <= 2.0:
        raise ConfigurationError(
            f"TEMPERATURE must be between 0.0 and 2.0, got {temperature}."
        )

    return Settings(
        gemini_api_key=api_key,
        gemini_model=model,
        temperature=temperature,
    )