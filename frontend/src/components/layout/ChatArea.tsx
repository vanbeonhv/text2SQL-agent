import { Send, Loader2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../../stores/useChatStore';
import { useChatStream } from '../../hooks/useChatStream';
import { useConversation } from '../../hooks/useConversations';
import { cn } from '../../lib/utils';
import { IconButton } from '../ui/IconButton';
import { UserMessage } from '../chat/UserMessage';
import { AssistantMessage } from '../chat/AssistantMessage';
import { TypingIndicator } from '../chat/TypingIndicator';
import type { Message } from '../../types/chat';

export const ChatArea = () => {
  const [input, setInput] = useState('');
  const { messages, isStreaming, activeConversationId, setMessages, setConversationMetadata, setIsLoadingHistory } = useChatStore();
  const { streamChat } = useChatStream();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { data, isLoading } = useConversation(activeConversationId);
  const showHistoryLoading = isLoading && !isStreaming;

  // Sync loading state into store so ConversationList can disable buttons
  useEffect(() => {
    setIsLoadingHistory(showHistoryLoading);
  }, [showHistoryLoading, setIsLoadingHistory]);

  // Sync React Query cached data into the store when conversation changes.
  // Skip while streaming so empty/partial GET responses do not wipe optimistic UI.
  useEffect(() => {
    if (!data || isStreaming) return;
    const mapped: Message[] = data.messages.map((msg) => ({
      id: `${data.id}-${msg.id}`,
      role: msg.role,
      content: msg.content,
      sql: msg.sql,
      results: msg.results,
      error: msg.error,
      metadata: msg.metadata,
      feedback: msg.feedback as 'like' | 'dislike' | null | undefined,
      timestamp: new Date(msg.timestamp).getTime(),
    }));
    setMessages(mapped);
    setConversationMetadata({
      id: data.id,
      title: data.title,
      created_at: data.created_at,
      updated_at: data.updated_at,
    });
  }, [data, isStreaming, setMessages, setConversationMetadata]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const question = input.trim();
    setInput('');

    await streamChat(question);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <main className="h-full min-h-0 flex flex-col overflow-hidden bg-light-bg dark:bg-dark-bg">
      {/* Messages area */}
      <div className="relative flex-1 overflow-y-auto px-4 py-6 min-h-0">
        {/* Loading overlay */}
        {showHistoryLoading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/60 dark:bg-[#0A0A0F]/60 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-3 rounded-xl border border-[#E9D5FF] dark:border-[#2D2D3A] bg-white dark:bg-[#1A1A24] px-8 py-6 shadow-lg">
              <Loader2 className="h-8 w-8 animate-spin text-purple-500 dark:text-purple-400" />
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Loading...</p>
            </div>
          </div>
        )}
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <h2 className="text-2xl font-heading font-semibold mb-2">
                Welcome to Text2SQL Agent
              </h2>
              <p className="text-muted">
                Ask me anything about your database and I'll help you write SQL queries
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                message.role === 'user'
                  ? <UserMessage key={message.id} message={message} />
                  : <AssistantMessage key={message.id} message={message} />
              ))}
              {isStreaming && <TypingIndicator />}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-default surface p-4 flex-shrink-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your database..."
                rows={1}
                disabled={isStreaming}
                className={cn(
                  'w-full px-4 py-3 pr-12 rounded-lg resize-none',
                  'surface elevated border border-default',
                  'focus:outline-none focus:ring-2 focus:ring-primary',
                  'placeholder:text-muted',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
            </div>
            <IconButton
              type="submit"
              variant="primary"
              size="lg"
              disabled={!input.trim() || isStreaming}
              aria-label="Send message"
            >
              <Send className="w-5 h-5" />
            </IconButton>
          </div>
        </form>
      </div>
    </main>
  );
};
