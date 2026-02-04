import { Tag } from 'lucide-react';
import { cn } from '../../lib/utils';

interface IntentBadgeProps {
  intent: string;
}

const intentColors: Record<string, string> = {
  data_retrieval: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  aggregation: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  filtering: 'bg-green-500/20 text-green-400 border-green-500/30',
  joining: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  sorting: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  grouping: 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
};

export const IntentBadge = ({ intent }: IntentBadgeProps) => {
  const colorClass = intentColors[intent] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';

  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-2">
        <Tag className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-medium">Detected Intent</h3>
      </div>
      <div
        className={cn(
          'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border',
          colorClass
        )}
      >
        {intent.replace(/_/g, ' ')}
      </div>
    </div>
  );
};
