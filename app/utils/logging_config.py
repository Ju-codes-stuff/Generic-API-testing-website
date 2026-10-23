"""Logging configuration for the application.

Provides a pre-configured logger that:
- Logs useful application events and errors for debugging.
- Never logs API keys or sensitive user conversation content.
"""

import logging
import sys


def get_logger(name: str = "qa_app") -> logging.Logger:
    """Return a configured logger instance.

    The logger writes to *stderr* so that it does not interfere with
    Streamlit's stdout-based rendering pipeline.

    Args:
        name: Logger name (defaults to ``"qa_app"``).

    Returns:
        A ``logging.Logger`` ready for use.
    """

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to the root logger to avoid duplicate output.
        logger.propagate = False

    return logger