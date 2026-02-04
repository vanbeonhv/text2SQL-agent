# Response Formatting System

## Overview

The response formatting system intelligently routes between Python-based formatting and LLM-based summarization based on query intent, optimizing for latency and cost while providing rich, helpful responses.

## Strategy

### 🚀 Fast Path: Python-Only (5ms)

**Used for:** Simple queries (data retrieval, filtering, sorting)

**Process:**
1. Format results to markdown table using Python
2. Add predefined opening based on intent
3. Include simple summary

**Example:**
```markdown
I found **15** records matching your criteria:

| id | name | price | category |
|---|---|---|---|
| 1 | Laptop | 999.99 | Electronics |
| 4 | Monitor | 299.99 | Electronics |
...

*Showing 15 of 15 results*
```

**Latency:** ~5ms  
**Cost:** $0 (no LLM calls)

---

### ⚡ Hybrid Path: Python + LLM Insights (350ms)

**Used for:** Aggregations and joins

**Process:**
1. **Parallel execution:**
   - Thread 1: Format table with Python (5ms)
   - Thread 2: Generate insights with lightweight model (300-800ms)
2. Combine table + insights

**Example:**
```markdown
Here's the summary:

| category | count | avg_price |
|---|---|---|
| Electronics | 120 | 349.99 |
| Furniture | 45 | 199.99 |

### 💡 Insights

The data shows Electronics dominating with 120 products at an average 
price of $350, while Furniture has fewer items but maintains competitive 
pricing at $200 average.
```

**Latency:** ~350ms (parallelized)  
**Cost:** ~$0.0001 (Flash model)

---

### 🤖 Full LLM Path: Complete Formatting (2s)

**Used for:** Complex/unknown queries

**Process:**
1. Send full context to thinking model
2. LLM generates complete markdown response
3. Includes opening, table, insights, and answer

**Latency:** ~2000ms  
**Cost:** ~$0.001 (Pro model)

---

## Model Tiers

### Thinking Model (gemini-1.5-pro)
**Used for:**
- SQL generation
- Error correction
- Complex response formatting

**Characteristics:**
- More accurate
- Slower (1500-3000ms)
- More expensive

### Lightweight Model (gemini-1.5-flash)
**Used for:**
- Insights generation
- Simple summaries

**Characteristics:**
- Fast (300-800ms)
- 3-5x faster than Pro
- 10x cheaper than Pro
- Still high quality for simple tasks

---

## Configuration

### Environment Variables

```bash
# Model Selection
THINKING_MODEL=gemini-1.5-pro        # For SQL generation
LIGHTWEIGHT_MODEL=gemini-1.5-flash   # For summaries

# Formatting Behavior
ENABLE_LLM_INSIGHTS=true             # Toggle insights for aggregations
FORMAT_WITH_LLM_THRESHOLD=100        # Rows > 100 always use Python
MAX_DISPLAY_ROWS=50                  # Max rows in markdown table
```

### Runtime Behavior

```python
# Fast path
if intent in ["data_retrieval", "filtering", "sorting"]:
    return python_format(result)  # 5ms

# Hybrid path
elif intent in ["aggregation", "joining"]:
    if enable_insights and count < threshold:
        table, insight = await asyncio.gather(
            python_format(result),
            llm_summarize(result)  # Lightweight model
        )
        return table + insight  # 350ms
    else:
        return python_format(result)  # 5ms

# Fallback
else:
    return llm_full_format(result)  # Thinking model, 2000ms
```

---

## Performance Comparison

| Query Type | Method | Latency | Cost | Quality |
|------------|--------|---------|------|---------|
| **Simple list** | Python | 5ms | $0 | Good |
| **With filter** | Python | 5ms | $0 | Good |
| **Aggregation (no insights)** | Python | 5ms | $0 | Good |
| **Aggregation (with insights)** | Hybrid | 350ms | $0.0001 | Excellent |
| **Complex** | Full LLM | 2000ms | $0.001 | Excellent |

**Savings:**
- **95% latency** for simple queries (5ms vs 2000ms)
- **82% latency** for aggregations (350ms vs 2000ms)
- **90% cost** by using Flash for summaries

---

## Example Output

### Simple Query
**User:** "Show me all products"  
**Intent:** data_retrieval  
**Method:** python  
**Latency:** 5ms

```markdown
Here are the results:

| id | name | price | category | stock |
|---|---|---|---|---|
| 1 | Laptop | 999.99 | Electronics | 15 |
| 2 | Mouse | 29.99 | Electronics | 50 |
| 3 | Keyboard | 79.99 | Electronics | 30 |
| 4 | Monitor | 299.99 | Electronics | 20 |
| 5 | Desk Chair | 199.99 | Furniture | 10 |

**Summary:** 5 rows returned.
```

---

### Aggregation with Insights
**User:** "What's the average price by category?"  
**Intent:** aggregation  
**Method:** hybrid  
**Latency:** 350ms

```markdown
Here's the summary:

| category | avg_price | product_count |
|---|---|---|
| Electronics | 352.49 | 4 |
| Furniture | 199.99 | 1 |

### 💡 Insights

Electronics products average $352, driven by high-ticket items like laptops 
and monitors. With 4 products in this category versus only 1 in Furniture, 
Electronics represents the core of the inventory at a premium price point.
```

---

### Complex Query
**User:** "Show sales trends and tell me what's interesting"  
**Intent:** unknown  
**Method:** llm  
**Latency:** 2000ms

```markdown
# Sales Trends Analysis

Looking at your sales data, here are the key findings:

| month | revenue | orders | avg_order |
|---|---|---|---|
| Jan | 45000 | 150 | 300 |
| Feb | 52000 | 165 | 315 |
| Mar | 61000 | 180 | 339 |

## Key Observations

1. **Strong Growth**: Revenue increased 35% from January to March
2. **Order Value**: Average order value grew from $300 to $339
3. **Volume**: Both order count and value are trending upward

The data suggests healthy business growth with improving unit economics.
```

---

## Client-Side Experience

### SSE Event Flow

```javascript
// 1. Raw results
event: result
data: {"rows": [...], "count": 15}

// 2. Formatted response (NEW!)
event: formatted_response
data: {
  "markdown": "I found **15** records...",
  "format_method": "hybrid",
  "has_llm_summary": true
}

// 3. Completion
event: complete
data: {"success": true}
```

### Displaying Formatted Response

```javascript
eventSource.addEventListener('formatted_response', (e) => {
  const data = JSON.parse(e.data);
  
  // Render markdown
  const rendered = markdownToHtml(data.markdown);
  document.getElementById('response').innerHTML = rendered;
  
  // Show formatting info
  console.log(`Formatted with: ${data.format_method}`);
  if (data.has_llm_summary) {
    console.log('Includes AI-generated insights');
  }
});
```

---

## Customization

### Adding Custom Templates

```python
# backend/app/tools/response_formatter.py

OPENING_TEMPLATES = {
    "data_retrieval": "Here are the results:",
    "my_custom_intent": "Custom opening for {count} items:",
}
```

### Adjusting Thresholds

```python
# More aggressive Python-only approach
FORMAT_WITH_LLM_THRESHOLD=50  # Use Python for >50 rows

# Always include insights
ENABLE_LLM_INSIGHTS=true

# More permissive display
MAX_DISPLAY_ROWS=100
```

### Custom Insight Prompts

```python
# backend/app/tools/response_formatter.py

async def generate_insight(self, ...):
    prompt = f"""Your custom prompt here
    
    Question: {question}
    Data: {sample_data}
    
    Focus on: [your specific criteria]
    """
```

---

## Testing

### Unit Tests

```python
# Test Python formatting
def test_python_formatter():
    formatter = PythonFormatter()
    result = {"rows": [...], "count": 5, "columns": ["id", "name"]}
    markdown = formatter.format_table(result, intent="filtering")
    assert "I found **5** records" in markdown
    assert "| id | name |" in markdown

# Test intent routing
async def test_response_formatter_routing():
    formatter = ResponseFormatter()
    
    # Simple query -> Python
    result1 = await formatter.format_response(
        question="Show products",
        intent="data_retrieval",
        ...
    )
    assert result1["format_method"] == "python"
    
    # Aggregation -> Hybrid
    result2 = await formatter.format_response(
        question="Average price by category",
        intent="aggregation",
        ...
    )
    assert result2["format_method"] == "hybrid"
```

### Integration Tests

```bash
# Test with real queries
python example_client.py

# Check latency
curl -N http://localhost:8000/api/chat/stream \
  -d '{"question": "Show all products"}' \
  | grep "formatted_response"
```

---

## Troubleshooting

### Insights Not Appearing

**Check:**
1. `ENABLE_LLM_INSIGHTS=true` in `.env`
2. Query intent is "aggregation" or "joining"
3. Result count < `FORMAT_WITH_LLM_THRESHOLD`
4. Lightweight model API key is valid

### Slow Response Times

**If all queries take 2s:**
- Check if falling back to full LLM formatting
- Verify intent analysis is working
- Check `format_method` in response

**If hybrid queries are slow:**
- Lightweight model may not be configured
- Check `LIGHTWEIGHT_MODEL` setting
- Verify parallel execution (should be ~350ms, not 2s)

### Formatting Errors

**If markdown is broken:**
- Check cell value escaping (pipes, newlines)
- Verify column names don't contain special chars
- Check for very long cell values (truncated at 100 chars)

---

## Future Enhancements

1. **Progressive Streaming**: Stream table first, insights later
2. **Chart Specifications**: Include Plotly/Chart.js configs in markdown
3. **Caching**: Cache formatted responses for identical queries
4. **Conditional Insights**: Only generate when user asks "why" or "insight"
5. **Custom Formatters**: Allow plugins for specific data types
6. **Language Detection**: Format numbers/dates based on user locale

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│      execute_sql_node                   │
│      Returns: rows, count, columns      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│      format_response_node                │
│  ┌────────────────────────────────────┐  │
│  │  ResponseFormatter.format_response │  │
│  └──────────┬─────────────────────────┘  │
│             │                             │
│      ┌──────▼──────┐                     │
│      │ Check Intent│                     │
│      └──────┬──────┘                     │
│             │                             │
│      ┌──────▼──────────────────────┐     │
│      │                             │     │
│  ┌───▼────┐  ┌────▼─────┐  ┌─────▼──┐  │
│  │ Simple │  │Aggregate │  │Complex │  │
│  │ Python │  │  Hybrid  │  │  LLM   │  │
│  │  5ms   │  │  350ms   │  │ 2000ms │  │
│  └───┬────┘  └────┬─────┘  └─────┬──┘  │
│      │            │               │     │
│      └────────────┴───────────────┘     │
│                   │                     │
│      ┌────────────▼──────────────┐      │
│      │  Formatted Markdown       │      │
│      └───────────────────────────┘      │
└──────────────┬──────────────────────────┘
               │
               ▼
        save_success_node
```

---

**Built with intelligent routing for optimal latency and cost!** 🚀
