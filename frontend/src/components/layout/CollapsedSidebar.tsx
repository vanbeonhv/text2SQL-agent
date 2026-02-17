import { Plus, Search } from 'lucide-react';
import { CollapseToggle } from '../ui/CollapseToggle';

interface CollapsedSidebarProps {
  onNewChat: () => void;
  leftExpanded: boolean;
  onToggleLeft: () => void;
}

export const CollapsedSidebar: React.FC<CollapsedSidebarProps> = ({
  onNewChat,
  leftExpanded,
  onToggleLeft,
}) => {
  return (
    <aside className="relative h-full surface border-r border-default flex flex-col items-center py-4 gap-4">
      <button
        className="w-10 h-10 rounded-lg hover:bg-light-elevated dark:hover:bg-dark-elevated flex items-center justify-center transition-colors cursor-pointer"
        aria-label="New chat"
        onClick={onNewChat}
      >
        <Plus className="w-5 h-5" />
      </button>
      <button
        className="w-10 h-10 rounded-lg hover:bg-light-elevated dark:hover:bg-dark-elevated flex items-center justify-center transition-colors cursor-pointer"
        aria-label="Search conversations"
      >
        <Search className="w-5 h-5" />
      </button>
      <CollapseToggle expanded={leftExpanded} onToggle={onToggleLeft} side="left" />
    </aside>
  );
};
