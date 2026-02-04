#!/usr/bin/env python3
"""Example client for testing the Text-to-SQL API."""
import httpx
import json
import sys


def stream_chat(question: str, conversation_id: str = None):
    """Stream chat response with progress updates.
    
    Args:
        question: User's question
        conversation_id: Optional conversation ID for multi-turn
    """
    url = "http://localhost:8000/api/chat/stream"
    payload = {"question": question}
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")
    
    current_conversation_id = None
    
    with httpx.Client(timeout=60.0) as client:
        with client.stream("POST", url, json=payload) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                
                # Parse SSE format
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        # Handle different event types
                        if event_type == "conversation_id":
                            current_conversation_id = data["conversation_id"]
                            print(f"📝 Conversation ID: {current_conversation_id}\n")
                        
                        elif event_type == "stage":
                            icon = data.get("icon", "🔄")
                            message = data.get("message", "Processing...")
                            print(f"{icon} {message}")
                        
                        elif event_type == "intent":
                            intent = data.get("intent", "unknown")
                            print(f"   Intent: {intent}")
                        
                        elif event_type == "similar_examples":
                            count = data.get("count", 0)
                            print(f"   Found {count} similar examples")
                        
                        elif event_type == "sql":
                            sql = data.get("sql", "")
                            print(f"\n📊 Generated SQL:")
                            print(f"   {sql}\n")
                        
                        elif event_type == "validation":
                            valid = data.get("valid", False)
                            if valid:
                                print("✓ Validation passed")
                            else:
                                errors = data.get("errors", [])
                                print(f"❌ Validation failed: {errors}")
                        
                        elif event_type == "result":
                            count = data.get("count", 0)
                            rows = data.get("rows", [])
                            print(f"📈 Results ({count} rows):")
                            
                            if rows:
                                # Print first few rows
                                for i, row in enumerate(rows[:5], 1):
                                    print(f"   {i}. {row}")
                                
                                if count > 5:
                                    print(f"   ... and {count - 5} more rows")
                            else:
                                print("   (No results)")
                        
                        elif event_type == "formatted_response":
                            markdown = data.get("markdown", "")
                            format_method = data.get("format_method", "unknown")
                            has_summary = data.get("has_llm_summary", False)
                            
                            print(f"\n{'='*60}")
                            print(f"📝 Formatted Response (method: {format_method})")
                            if has_summary:
                                print("   (includes LLM-generated insights)")
                            print(f"{'='*60}\n")
                            print(markdown)
                            print(f"\n{'='*60}")
                        
                        elif event_type == "error":
                            error = data.get("error", "Unknown error")
                            retry = data.get("retry_count", 0)
                            print(f"❌ Error (retry {retry}): {error}")
                        
                        elif event_type == "complete":
                            success = data.get("success", False)
                            if success:
                                print(f"\n✅ Query completed successfully!\n")
                            else:
                                print(f"\n❌ Query failed\n")
                    
                    except json.JSONDecodeError:
                        pass
    
    return current_conversation_id


def main():
    """Run example queries."""
    print("🤖 Text-to-SQL Agent Example Client")
    print("="*60)
    
    # Example 1: Simple query
    conv_id = stream_chat("Show me all products")
    
    # Example 2: Multi-turn conversation
    if conv_id:
        print("\n💬 Continuing conversation...")
        stream_chat("Only show products with price > 100", conversation_id=conv_id)
        stream_chat("Sort them by price", conversation_id=conv_id)
    
    # Example 3: Aggregation query
    stream_chat("How many products are in stock?")
    
    # Example 4: Join query
    stream_chat("Show me all orders with product names")
    
    print("\n✨ Done! Check out the API docs at http://localhost:8000/docs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the server is running:")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)
