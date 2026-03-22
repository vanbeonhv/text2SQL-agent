# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack AI chatbot that converts natural language to SQL using LangGraph + FastAPI (backend) and React 18 + TypeScript (frontend). Uses SSE streaming for real-time progress visualization.

## Commands

### Backend (Python 3.11 required)
```bash
cd backend
uv venv --python 3.11 && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in GEMINI_API_KEY
python -m app.database.init_db
./run.sh              # starts at http://localhost:8000
```

```bash
pytest                # run all tests
pytest tests/test_foo.py::test_bar  # run single test
```

### Frontend (Node 18+, pnpm)
```bash
cd frontend
pnpm install
cp .env.example .env  # VITE_API_URL=http://localhost:8000
pnpm dev              # dev server at http://localhost:5173
pnpm build            # production build
pnpm lint             # ESLint
```

## Architecture

### Backend: LangGraph Workflow

The agent runs as a directed graph (`backend/app/agents/graph.py`) with these nodes in order:

```
load_conversation → analyze_intent → retrieve_schema → search_history
→ generate_sql → validate_sql → execute_sql → format_response → save_success
                             ↘ fail (invalid SQL)
                                          ↘ correct_error → [retry validate_sql, or fail]
```

- **AgentState** (`app/models/state.py`) — TypedDict that flows through all nodes
- **Node implementations** (`app/agents/nodes.py`) — one function per graph node
- **Tools** (`app/tools/`) — intent_analyzer, sql_writer, sql_validator, sql_executor, error_corrector, response_formatter

### LLM Gateway

`app/services/llm_gateway/` provides a provider-agnostic interface (`base.py`) with a Gemini implementation (`gemini.py`). Uses dual model tiers: `THINKING_MODEL` for SQL generation, `LIGHTWEIGHT_MODEL` for summaries. Factory pattern in `factory.py` for switching providers.

### Databases

Two SQLite databases:
- **`history.db`** — conversation messages + successful query history (used for few-shot learning via Levenshtein similarity search)
- **`target.db`** — the user's actual database being queried (initialized from `data/schema.json`)

Connection management via async aiosqlite in `app/database/connection.py`.

### API

Single streaming endpoint: `POST /api/chat/stream` — returns SSE with 11 event types:
`conversation_id`, `stage`, `intent`, `schema`, `similar_examples`, `sql`, `validation`, `result`, `error`, `formatted_response`, `complete`

### Frontend State & Streaming

- **Zustand stores** (`src/stores/`) — `useChatStore` (messages/conversation), `useProcessStore` (SSE stage timeline), `useSidebarStore`, `useThemeStore`
- **SSE hook** (`src/hooks/useChatStream.ts`) — handles all 11 event types, updates stores in real-time
- **Visualizer components** (`src/components/visualizer/`) — render the real-time process timeline shown in the right sidebar

## Configuration

Backend config is Pydantic Settings in `app/config.py`. Key `.env` variables:
- `LLM_PROVIDER` (gemini/openai/claude), `GEMINI_API_KEY`
- `THINKING_MODEL`, `LIGHTWEIGHT_MODEL`
- `MAX_RETRY_ATTEMPTS` (default 3), `QUERY_TIMEOUT_SECONDS` (30), `MAX_ROWS_RETURN` (1000)

## SQL Safety

`app/tools/sql_validator.py` enforces: SELECT-only, keyword blacklist (UPDATE/DELETE/DROP/INSERT/ALTER/TRUNCATE/etc.), no SQL comments, no multiple statements.
