import { Tag } from 'lucide-react';
import { cn } from '../../lib/utils';

interface IntentBadgeProps {
  intent: string;
}

const intentBadgeClass =
  'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border bg-primary/20 text-primary border-primary/30';

export const IntentBadge = ({ intent }: IntentBadgeProps) => {
  return (
    <div className="surface elevated rounded-lg p-4 border border-default">
      <div className="flex items-center gap-2 mb-2">
        <Tag className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-medium">Detected Intent</h3>
      </div>
      <div className={cn(intentBadgeClass)}>
        {intent.replace(/_/g, ' ')}
      </div>
    </div>
  );
};
