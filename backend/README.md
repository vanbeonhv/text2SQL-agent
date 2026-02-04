# Text-to-SQL Chatbot Backend

AI-powered chatbot that converts natural language questions into SQL queries using LangGraph and LLM Gateway (Gemini/OpenAI/Claude).

## Features

- 🤖 **LLM Gateway**: Multi-provider abstraction (Gemini, OpenAI, Claude)
- 💬 **Conversation Memory**: Context-aware multi-turn conversations
- 📚 **Few-Shot Learning**: Learn from historical successful queries
- 🔄 **Auto-Retry**: Automatic SQL error correction (up to 3 attempts)
- 🔒 **SQL Validation**: Only SELECT queries allowed (safety-first)
- 📊 **Real-time Streaming**: SSE with progress updates at each stage
- 🎯 **Intent Analysis**: Understand user's question intent
- 🔍 **Similarity Search**: Find related past queries for better context

## Architecture

```
User Question → Load Conversation → Intent Analysis → Schema Retrieval 
→ Find Similar Q&A → Generate SQL → Validate → Execute → Return Results
```

All stages stream progress updates to the client in real-time.

## Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Initialize databases:**
```bash
python -m app.database.init_db
```

4. **Run the server:**
```bash
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

### Chat (Streaming)
```bash
POST /api/chat/stream
Body: {
  "question": "Show me all products with price > 100",
  "conversation_id": "optional-uuid"
}

Response: SSE stream with events:
- conversation_id
- stage (progress updates)
- intent, schema, sql, result, complete
```

### Get Conversation History
```bash
GET /api/conversations/{conversation_id}
```

### Health Check
```bash
GET /api/health
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── constants.py         # Stage messages and constants
│   ├── models/              # Pydantic models
│   ├── database/            # Database operations
│   ├── agents/              # LangGraph workflow
│   ├── tools/               # Agent tools (SQL writer, validator, etc.)
│   ├── services/            # Business logic services
│   │   ├── llm_gateway/     # Multi-provider LLM abstraction
│   │   ├── conversation.py  # Conversation memory
│   │   └── history_search.py # Similar query search
│   └── api/                 # API routes
├── tests/                   # Unit and integration tests
└── data/                    # Databases and schema files
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/ tests/
```

## License

MIT
