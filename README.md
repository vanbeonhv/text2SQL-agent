# Text2SQL Agent

AI-powered chatbot that converts natural language questions into SQL queries using LangGraph, with a modern React frontend.

## Project Structure

```
text2SQL-agent/
├── backend/          # FastAPI + LangGraph backend with SSE streaming
└── frontend/         # React 18 + TypeScript frontend with AI Modern theme
```

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
python -m app.database.init_db
./run.sh
```

Backend will run at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

Frontend will run at `http://localhost:5173`

## Features

### Backend
- ✅ LLM Gateway (Gemini/OpenAI/Claude support)
- ✅ Conversation memory with SQLite
- ✅ Few-shot learning with similarity search
- ✅ Agent tools (Intent Analyzer, SQL Writer, Validator, Executor, Error Corrector)
- ✅ LangGraph workflow with 10 processing nodes
- ✅ Real-time SSE streaming with 11 event types
- ✅ FastAPI with interactive docs at `/docs`

### Frontend
- ✅ Modern AI Modern theme (purple-cyan)
- ✅ Dark/Light mode with system preference detection
- ✅ Fully responsive (desktop, tablet, mobile)
- ✅ SSE streaming with process visualizer
- ✅ SQL syntax highlighting with Shiki
- ✅ Collapsible sidebars (chat history + process)
- ✅ Keyboard shortcuts and accessibility
- ✅ React Query for server state
- ✅ Zustand for client state

## Documentation

- [Backend README](backend/README.md) - Backend setup and API docs
- [Frontend README](frontend/README.md) - Frontend setup and features
- [Project Summary](PROJECT_SUMMARY.md) - Complete project overview
- [Frontend Implementation](frontend/IMPLEMENTATION_SUMMARY.md) - Frontend details

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- LangGraph
- Gemini API (Google AI)
- SQLite
- Uvicorn

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS 4
- Zustand
- React Query
- Shiki

## Architecture

```
┌─────────────┐
│   React     │
│  Frontend   │
└──────┬──────┘
       │ SSE Stream
       ▼
┌─────────────────────────────────┐
│      FastAPI Backend            │
│  ┌──────────────────────────┐  │
│  │   LangGraph Workflow     │  │
│  │  1. Load Conversation    │  │
│  │  2. Analyze Intent       │  │
│  │  3. Retrieve Schema      │  │
│  │  4. Search History       │  │
│  │  5. Generate SQL         │◄─┼─── LLM Gateway
│  │  6. Validate SQL         │  │    (Gemini)
│  │  7. Execute SQL          │  │
│  │  8. Correct Errors       │  │
│  │  9. Save Success         │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
       │              │
       ▼              ▼
┌─────────────┐  ┌─────────────┐
│  history.db │  │  target.db  │
└─────────────┘  └─────────────┘
```

## API Endpoints

- `POST /api/chat/stream` - SSE streaming chat
- `GET /api/conversations/{id}` - Get conversation history
- `GET /api/health` - Health check

## License

MIT
