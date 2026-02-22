import { useState, useCallback } from 'react';
import { useChatStore } from '../stores/useChatStore';
import { useProcessStore } from '../stores/useProcessStore';
import { api } from '../services/api';
import type { SSEEvent } from '../types/events';

export const useChatStream = () => {
  const [error, setError] = useState<string | null>(null);
  const { addMessage, setIsStreaming, activeConversationId, updateLastMessage, setActiveConversation } = useChatStore();
  const { updateFromSSE, resetProcess } = useProcessStore();

  const streamChat = useCallback(async (question: string) => {
    setError(null);
    setIsStreaming(true);
    resetProcess();

    // Add user message immediately
    addMessage({
      role: 'user',
      content: question,
    });

    // Add placeholder for assistant message
    addMessage({
      role: 'assistant',
      content: '',
    });

    try {
      const response = await api.streamChat(question, activeConversationId || undefined);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let buffer = '';
      let finalSQL = '';
      let finalResults: any = null;
      let formattedMarkdown = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const [eventLine, dataLine] = line.split('\n');
            if (!eventLine || !dataLine) continue;

            const eventType = eventLine.replace('event: ', '').trim();
            const data = JSON.parse(dataLine.replace('data: ', ''));

            // Update process store for visualizer
            const sseEvent: SSEEvent = {
              type: eventType as any,
              data,
            };
            updateFromSSE(sseEvent);

            // Capture SQL and results for the message
            if (eventType === 'conversation_id') {
              setActiveConversation(data.conversation_id);
            } else if (eventType === 'sql') {
              finalSQL = data.sql;
              updateLastMessage({ sql: finalSQL });
            } else if (eventType === 'result') {
              finalResults = {
                rows: data.rows,
                count: data.count,
                columns: data.columns,
              };
              updateLastMessage({ results: finalResults });
            } else if (eventType === 'formatted_response') {
              formattedMarkdown = data.markdown || '';
              updateLastMessage({
                content: formattedMarkdown,
                metadata: {
                  format_method: data.format_method,
                  has_llm_summary: data.has_llm_summary,
                },
              });
            } else if (eventType === 'complete') {
              updateLastMessage({
                content: formattedMarkdown || (finalSQL ? 'Query completed' : 'No response generated'),
                sql: finalSQL || undefined,
                results: finalResults,
              });
            } else if (eventType === 'error') {
              updateLastMessage({
                content: 'Error occurred',
                error: data.error,
              });
            }
          } catch (parseError) {
            console.error('Error parsing SSE event:', parseError);
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      updateLastMessage({
        content: 'Failed to process query',
        error: errorMessage,
      });
    } finally {
      setIsStreaming(false);
    }
  }, [
    activeConversationId,
    addMessage,
    setIsStreaming,
    setActiveConversation,
    updateFromSSE,
    resetProcess,
    updateLastMessage,
  ]);

  return {
    streamChat,
    error,
  };
};
