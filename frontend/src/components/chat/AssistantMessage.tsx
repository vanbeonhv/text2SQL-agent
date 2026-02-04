import { Avatar } from '../ui/Avatar';
import { Database, AlertCircle } from 'lucide-react';
import type { Message } from '../../types/chat';
import { SQLCodeBlock } from '../sql/SQLCodeBlock';

interface AssistantMessageProps {
  message: Message;
}

export const AssistantMessage = ({ message }: AssistantMessageProps) => {
  return (
    <div className="flex gap-3 justify-start">
      <Avatar fallback="AI" size="sm" className="bg-accent" />
      <div className="max-w-[80%] space-y-3">
        {/* Main content */}
        {message.content && (
          <div className="surface elevated rounded-lg px-4 py-3">
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        )}

        {/* SQL Query */}
        {message.sql && (
          <div className="surface elevated rounded-lg overflow-hidden border border-default">
            <div className="px-4 py-2 border-b border-default bg-light-elevated dark:bg-dark-elevated flex items-center gap-2">
              <Database className="w-4 h-4 text-primary" />
              <span className="text-xs font-medium">Generated SQL</span>
            </div>
            <SQLCodeBlock code={message.sql} showCopy={true} />
          </div>
        )}

        {/* Results Table Preview */}
        {message.results && message.results.rows.length > 0 && (
          <div className="surface elevated rounded-lg overflow-hidden border border-default">
            <div className="px-4 py-2 border-b border-default bg-light-elevated dark:bg-dark-elevated">
              <span className="text-xs font-medium">
                Results ({message.results.count} rows)
              </span>
            </div>
            <div className="overflow-x-auto max-h-64">
              <table className="w-full text-xs">
                <thead className="bg-light-elevated dark:bg-dark-elevated sticky top-0">
                  <tr>
                    {message.results.columns?.map((col) => (
                      <th key={col} className="px-3 py-2 text-left font-medium border-b border-default">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {message.results.rows.slice(0, 10).map((row, idx) => (
                    <tr key={idx} className="hover:bg-light-elevated dark:hover:bg-dark-elevated">
                      {message.results?.columns?.map((col) => (
                        <td key={col} className="px-3 py-2 border-b border-default">
                          {row[col] !== null && row[col] !== undefined 
                            ? String(row[col]) 
                            : <span className="text-muted italic">null</span>
                          }
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {message.results.count > 10 && (
              <div className="px-4 py-2 border-t border-default bg-light-elevated dark:bg-dark-elevated text-xs text-muted text-center">
                Showing 10 of {message.results.count} rows
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {message.error && (
          <div className="surface elevated rounded-lg px-4 py-3 border border-error bg-error/10">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
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
