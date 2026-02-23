import { Avatar } from '../ui/Avatar';
import { AlertCircle, Database, ThumbsUp, ThumbsDown } from 'lucide-react';
import type { Message } from '../../types/chat';
import { SQLCodeBlock } from '../sql/SQLCodeBlock';
import { useChatStore } from '../../stores/useChatStore';
import { api } from '../../services/api';
import { cn } from '../../lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface AssistantMessageProps {
  message: Message;
}

export const AssistantMessage = ({ message }: AssistantMessageProps) => {
  const { setMessageFeedback, activeConversationId } = useChatStore();

  const handleFeedback = async (status: 'like' | 'dislike') => {
    if (!message.sql || !activeConversationId) return;

    // Toggle off if clicking the active status
    const next = message.feedback === status ? null : status;

    setMessageFeedback(message.id, next);

    try {
      await api.submitFeedback(message.sql, next ?? 'none', activeConversationId);
    } catch (e) {
      console.error('Failed to submit feedback:', e);
      // Revert optimistic update on failure
      setMessageFeedback(message.id, message.feedback ?? null);
    }
  };

  return (
    <div className="flex gap-3 justify-start">
      <Avatar fallback="AI" size="sm" className="bg-accent" />
      <div className="max-w-[80%] space-y-3">
        {/* Main content — rendered as markdown */}
        {message.content && (
          <div className="surface elevated rounded-lg px-4 py-3 text-sm">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ children }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="w-full text-xs border-collapse">{children}</table>
                  </div>
                ),
                thead: ({ children }) => (
                  <thead className="bg-light-elevated dark:bg-dark-elevated">{children}</thead>
                ),
                th: ({ children }) => (
                  <th className="px-3 py-2 text-left font-medium border border-default">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-3 py-2 border border-default">{children}</td>
                ),
                code: ({ children }) => (
                  <code className="bg-light-elevated dark:bg-dark-elevated px-1 rounded text-xs font-mono">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-light-elevated dark:bg-dark-elevated p-3 rounded-lg overflow-x-auto my-2 text-xs font-mono">
                    {children}
                  </pre>
                ),
                strong: ({ children }) => (
                  <strong className="font-semibold">{children}</strong>
                ),
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>
                ),
                h3: ({ children }) => (
                  <h3 className="font-semibold text-sm mt-3 mb-1">{children}</h3>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>

            {/* Like / Dislike — only for messages with SQL */}
            {message.sql && (
              <div className="flex gap-2 justify-end mt-3 pt-2 border-t border-default">
                <button
                  onClick={() => handleFeedback('like')}
                  title="Good response"
                  className={cn(
                    'p-1.5 rounded transition-colors',
                    message.feedback === 'like'
                      ? 'text-green-500 bg-green-500/10'
                      : 'text-muted hover:text-green-500 hover:bg-green-500/10'
                  )}
                >
                  <ThumbsUp className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleFeedback('dislike')}
                  title="Bad response"
                  className={cn(
                    'p-1.5 rounded transition-colors',
                    message.feedback === 'dislike'
                      ? 'text-red-500 bg-red-500/10'
                      : 'text-muted hover:text-red-500 hover:bg-red-500/10'
                  )}
                >
                  <ThumbsDown className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* SQL Query */}
        {message.sql && (
          <div className="surface rounded-lg overflow-hidden border border-default">
            <div className="px-4 py-2 border-b border-default surface flex items-center gap-2">
              <Database className="w-4 h-4 text-primary" />
              <span className="text-xs font-medium">Generated SQL</span>
            </div>
            <SQLCodeBlock code={message.sql} showCopy={true} />
          </div>
        )}

        {/* Error */}
        {message.error && (
          <div className="surface elevated rounded-lg px-4 py-3 border border-error bg-error/10">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-error shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-error">Error</p>
                <p className="text-xs text-muted mt-1">{message.error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
