import { History, Code } from 'lucide-react';
import type { SimilarExamplesEvent } from '../../types/events';

interface SimilarExamplesCardsProps {
  examples: SimilarExamplesEvent;
}

export const SimilarExamplesCards = ({ examples }: SimilarExamplesCardsProps) => {
  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-3">
        <History className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-medium">Similar Past Queries</h3>
        <span className="ml-auto text-xs text-muted">{examples.count} found</span>
      </div>

      <div className="space-y-2">
        {examples.examples.slice(0, 3).map((example: any, idx: number) => (
          <div
            key={idx}
            className="p-3 rounded-lg border border-default hover:border-primary/50 transition-colors"
          >
            <p className="text-xs text-muted mb-2">{example.question || 'Question'}</p>
            <div className="flex items-start gap-2">
              <Code className="w-3 h-3 text-accent mt-0.5 flex-shrink-0" />
              <code className="text-xs font-code text-accent break-all">
                {example.sql || example.query || 'SELECT ...'}
              </code>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
