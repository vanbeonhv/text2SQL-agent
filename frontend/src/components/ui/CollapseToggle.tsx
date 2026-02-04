import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../../lib/utils';

interface CollapseToggleProps {
  expanded: boolean;
  onToggle: () => void;
  side: 'left' | 'right';
  className?: string;
}

export const CollapseToggle = ({ expanded, onToggle, side, className }: CollapseToggleProps) => {
  const Icon = side === 'left' 
    ? (expanded ? ChevronLeft : ChevronRight)
    : (expanded ? ChevronRight : ChevronLeft);

  return (
    <button
      onClick={onToggle}
      className={cn(
        'absolute top-1/2 -translate-y-1/2 z-10',
        'w-6 h-12 rounded-full',
        'surface elevated border border-default',
        'flex items-center justify-center',
        'transition-all duration-300',
        'hover:scale-110 cursor-pointer',
        'focus:outline-none focus:ring-2 focus:ring-primary',
        side === 'left' ? '-right-3' : '-left-3',
        className
      )}
      aria-label={`${expanded ? 'Collapse' : 'Expand'} ${side} sidebar`}
    >
      <Icon className="w-4 h-4" />
    </button>
  );
};
