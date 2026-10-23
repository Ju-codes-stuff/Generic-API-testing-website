# 🤖 AI Question & Answering System

A production-quality Question & Answering application powered by **Google Gemini** models with a **Streamlit** chat interface.

---

## Overview

This application provides an interactive chat interface where users can ask questions and receive AI-generated answers. It maintains conversation history within a session, enabling natural follow-up questions — similar to ChatGPT.

## Features

- **ChatGPT-style interface** — Streamlit chat components with user/assistant message bubbles.
- **Conversation memory** — Follow-up questions leverage the full conversation history.
- **Configurable model** — Switch between Gemini models via environment variables.
- **Adjustable temperature** — Control response creativity through configuration.
- **Graceful error handling** — Friendly messages for auth failures, quota limits, and network issues.
- **Security-first** — API keys are never hard-coded, logged, or displayed in the UI.
- **Modular architecture** — Clean separation of UI, service, configuration, and prompt layers.
- **Comprehensive tests** — Fully mocked unit tests that run without a real API key.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit UI (main.py)                  │
│  • Chat input / output    • Session state management    │
│  • Sidebar controls       • Loading indicators          │
├─────────────────────────────────────────────────────────┤
│              Gemini Service (gemini_service.py)           │
│  • API communication      • Error handling              │
├─────────────────────────────────────────────────────────┤
│  Configuration (settings.py)  │  Prompts (qa_prompt.py) │
│  • Env-var loading            │  • System prompt         │
│  • Validation                 │    definition            │
├───────────────────────────────┴─────────────────────────┤
│              Utilities (logging_config.py)               │
│  • Structured logging     • No sensitive data in logs   │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
question_answering_app/
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # Streamlit UI entry-point
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Environment-based configuration
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py    # Google Gemini API wrapper
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── qa_prompt.py         # System prompt definition
│   │
│   └── utils/
│       ├── __init__.py
│       └── logging_config.py    # Logging setup
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py           # Configuration tests
│   └── test_gemini_service.py   # Service layer tests
│
├── .env.example                 # Template for environment variables
├── .gitignore
├── requirements.txt
├── README.md
└── run.sh                       # Convenience launcher (macOS/Linux)
```

## Prerequisites

| Requirement | Minimum Version |
|-------------|----------------|
| Python      | 3.10+          |
| pip         | 22.0+          |
| Google AI Studio account | with API key |

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd question_answering_app
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

**Activate it:**

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example file
cp .env.example .env      # macOS / Linux
copy .env.example .env     # Windows
```

Edit `.env` and replace the placeholder with your real Gemini API key:

```dotenv
GEMINI_API_KEY=your-real-api-key-here
GEMINI_MODEL=gemini-2.0-flash
TEMPERATURE=0.2
```

> **⚠️ Never commit `.env` to version control.** The `.gitignore` already excludes it.

### 5. Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Navigate to **Get API key** and create a new key.
4. Copy the key into your `.env` file.

## Running the Application

```bash
streamlit run app/main.py
```

Or on macOS/Linux:

```bash
bash run.sh
```

The app will open in your browser at `http://localhost:8501`.

## Running Tests

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

All tests are fully mocked and **do not require a real Gemini API key**.

## Example Questions

| Category | Example |
|----------|---------|
| General knowledge | *What causes the Northern Lights?* |
| Programming | *Explain Python decorators with an example.* |
| Follow-up | *Can you show a more advanced example?* |
| Science | *How does mRNA vaccination work?* |
| Math | *Derive the quadratic formula step by step.* |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"GEMINI_API_KEY is not configured"** | Create a `.env` file (see Setup §4). |
| **"Authentication failed"** | Verify your API key is correct and not expired. |
| **"Rate limit or quota exceeded"** | Wait a moment or check your Google AI Studio usage. |
| **"Unable to reach the Gemini API"** | Check your internet connection / firewall. |
| **App won't start** | Ensure the virtual environment is activated and dependencies are installed. |
| **Import errors** | Run the app from the project root: `streamlit run app/main.py`. |

## Security Considerations

- The API key is loaded from `.env` at runtime — **never** hard-coded.
- `.env` is excluded from version control via `.gitignore`.
- Error messages displayed to the user never contain the API key or internal stack traces.
- Logging never records the API key or full conversation content.
- The `Settings` dataclass is frozen (immutable) to prevent accidental mutation.

## Stopping the Application

Press `Ctrl+C` in the terminal where Streamlit is running.

## Deactivating the Virtual Environment

```bash
deactivate
```

## Future Enhancements

- **Streaming responses** — Use the Gemini streaming API for real-time token-by-token output.
- **Conversation export** — Allow users to download their chat history as Markdown or PDF.
- **Multiple conversations** — Support named conversation tabs.
- **Token usage tracking** — Display token counts and estimated cost per response.
- **Response caching** — Cache identical questions to reduce API costs.
- **User authentication** — Add login to persist conversations across sessions.
- **Custom system prompts** — Let users configure the assistant personality via the sidebar.
- **File/document upload** — Support Retrieval-Augmented Generation (RAG) over user documents.
- **Deployment** — Containerise with Docker and deploy to a cloud platform.

---

*Built with [Streamlit](https://streamlit.io/) and [Google Gemini](https://ai.google.dev/).*
