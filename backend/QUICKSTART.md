# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or use your favorite editor
```

Required configuration:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Initialize Databases

```bash
python -m app.database.init_db
```

This creates:
- `data/history.db` - Conversation memory and query history
- `data/target.db` - Example database (products and orders)
- `data/schema.json` - Database schema file

### 4. Start the Server

```bash
# Option 1: Using the run script
./run.sh

# Option 2: Direct uvicorn command
uvicorn app.main:app --reload --port 8000
```

Server will start at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Chat request (streaming)
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me all products"}'
```

### Using Python Client

```python
import httpx

# Create a streaming request
with httpx.Client() as client:
    with client.stream(
        "POST",
        "http://localhost:8000/api/chat/stream",
        json={"question": "Show me all products with price > 100"}
    ) as response:
        for line in response.iter_lines():
            if line.startswith("data: "):
                print(line[6:])
```

### Using the Example Client

```bash
python example_client.py
```

## Example Questions

Try these questions with the example database:

1. **Simple retrieval**: "Show me all products"
2. **Filtering**: "What products cost more than 100?"
3. **Aggregation**: "How many products are in stock?"
4. **Sorting**: "Show me the most expensive products"
5. **Joining**: "Show me all orders with product names"
6. **Multi-turn**: 
   - "Show me all products"
   - "Only the ones in Electronics category"
   - "Sort by price"

## API Endpoints

### POST /api/chat/stream
Stream chat response with progress updates.

**Request:**
```json
{
  "question": "Show me all products",
  "conversation_id": "optional-uuid"
}
```

**Response:** Server-Sent Events (SSE) stream
```
event: conversation_id
data: {"conversation_id": "abc-123"}

event: stage
data: {"stage": "analyzing_intent", "message": "Analyzing your question..."}

event: sql
data: {"sql": "SELECT * FROM products", "explanation": "..."}

event: result
data: {"rows": [...], "count": 5}

event: complete
data: {"success": true}
```

### GET /api/conversations/{id}
Get full conversation history.

**Response:**
```json
{
  "id": "abc-123",
  "created_at": "2024-01-01T00:00:00",
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ]
}
```

### GET /api/health
Health check.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Architecture

The system follows this flow:

1. **Load Conversation** - Load message history for context
2. **Analyze Intent** - Understand question intent (filtering, aggregation, etc.)
3. **Retrieve Schema** - Load database schema
4. **Search History** - Find similar past queries (few-shot learning)
5. **Generate SQL** - Create SQL with LLM using all context
6. **Validate SQL** - Ensure only SELECT queries (security)
7. **Execute SQL** - Run query with timeout/row limits
8. **Error Correction** - If fails, auto-retry with corrections (max 3 times)
9. **Save History** - Store successful queries for future learning

All stages stream real-time progress updates to the client!

## Customization

### Add Your Own Database

1. Create your SQLite database in `data/your_db.db`
2. Update `TARGET_DB_PATH` in `.env`
3. Create matching `schema.json`:

```json
{
  "tables": [
    {
      "name": "your_table",
      "columns": [
        {"name": "id", "type": "INTEGER", "primary_key": true},
        {"name": "name", "type": "TEXT"}
      ]
    }
  ],
  "relationships": []
}
```

### Change LLM Provider

Currently supports Gemini. To add OpenAI/Claude:

1. Implement provider in `app/services/llm_gateway/openai.py`
2. Update factory in `app/services/llm_gateway/factory.py`
3. Set `LLM_PROVIDER=openai` in `.env`

## Troubleshooting

**Error: "Gemini API key is required"**
- Make sure you set `GEMINI_API_KEY` in `.env`

**Error: "Database not found"**
- Run `python -m app.database.init_db`

**SQL validation fails**
- Only SELECT queries are allowed (security feature)
- Check for blocked keywords: UPDATE, DELETE, DROP, etc.

**Port 8000 already in use**
- Change port: `uvicorn app.main:app --port 8001`

## Next Steps

- Add your own database schema
- Try multi-turn conversations
- Explore the interactive docs at `/docs`
- Check out the source code structure in README.md

Happy querying! 🎉
