"""AI Question & Answering System – Streamlit UI.

This module implements the chat-style frontend. All Gemini communication is
delegated to :mod:`app.services.gemini_service`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that `app.*` imports resolve
# correctly when Streamlit runs this file as a script.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from app.config.settings import ConfigurationError, load_settings
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────────────


def _initialise_session_state() -> None:
    """Ensure all required session-state keys exist."""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "service" not in st.session_state:
        st.session_state.service = None

    if "settings" not in st.session_state:
        st.session_state.settings = None

    if "config_error" not in st.session_state:
        st.session_state.config_error = None


def _load_service() -> None:
    """Load settings and create the Gemini service (once per session)."""

    if st.session_state.service is not None:
        return

    try:
        settings = load_settings()
        st.session_state.settings = settings
        st.session_state.service = GeminiService(settings)
        st.session_state.config_error = None
        logger.info("Service loaded successfully.")
    except ConfigurationError as exc:
        st.session_state.config_error = str(exc)
        logger.error("Configuration error: %s", exc)


def _build_api_messages() -> list[dict[str, str]]:
    """Build the conversation message list for the API call."""

    return [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]


def _display_chat_history() -> None:
    """Render every message in the conversation history."""

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _clear_conversation() -> None:
    """Reset the conversation history."""

    st.session_state.messages = []
    logger.info("Conversation cleared by user.")


# ──────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────


def _render_sidebar() -> None:
    """Render the sidebar with model info and the Clear button."""

    with st.sidebar:
        st.header("⚙️ Settings")

        if st.session_state.settings:
            st.markdown(f"**Model:** `{st.session_state.settings.gemini_model}`")
            st.markdown(f"**Temperature:** `{st.session_state.settings.temperature}`")
        else:
            st.info("Model information will appear once configured.")

        st.divider()

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            _clear_conversation()
            st.rerun()

        st.divider()
        st.caption("Built with Streamlit & Google Gemini")


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────


def main() -> None:
    """Entry-point for the Streamlit application."""

    st.set_page_config(
        page_title="AI Q&A System",
        page_icon="🤖",
        layout="centered",
    )

    _initialise_session_state()
    _load_service()

    # ── Header ────────────────────────────────────────────────────────
    st.title("🤖 AI Question & Answering System")
    st.markdown(
        "Ask any question and get an answer powered by a **Google Gemini** model. "
        "The conversation history is maintained so you can ask follow-up questions."
    )

    # ── Sidebar ───────────────────────────────────────────────────────
    _render_sidebar()

    # ── Configuration error gate ──────────────────────────────────────
    if st.session_state.config_error:
        st.error(f"⚠️ **Configuration Error:** {st.session_state.config_error}")
        st.stop()

    # ── Chat history ──────────────────────────────────────────────────
    _display_chat_history()

    # ── Chat input ────────────────────────────────────────────────────
    if user_input := st.chat_input("Type your question here…"):
        # Validate: reject blank / whitespace-only input.
        question = user_input.strip()
        if not question:
            st.warning("Please enter a non-empty question.")
            st.stop()

        # Display and store the user message.
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Generate the assistant response.
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    api_messages = _build_api_messages()
                    answer = st.session_state.service.get_answer(api_messages)
                except GeminiServiceError as exc:
                    answer = f"⚠️ {exc}"
                    logger.error("GeminiServiceError surfaced to user: %s", exc)

            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
