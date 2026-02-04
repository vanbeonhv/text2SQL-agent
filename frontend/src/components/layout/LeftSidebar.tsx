import { useSidebarStore } from '../../stores/useSidebarStore';
import { CollapseToggle } from '../ui/CollapseToggle';
import { cn } from '../../lib/utils';
import { MessageSquare, Search, Plus } from 'lucide-react';
import { Button } from '../ui/Button';

export const LeftSidebar = () => {
  const { leftExpanded, toggleLeft } = useSidebarStore();

  if (!leftExpanded) {
    return (
      <aside className="relative h-full surface border-r border-default flex flex-col items-center py-4 gap-4">
        <button
          className="w-10 h-10 rounded-lg hover:bg-light-elevated dark:hover:bg-dark-elevated flex items-center justify-center transition-colors cursor-pointer"
          aria-label="New chat"
        >
          <Plus className="w-5 h-5" />
        </button>
        <button
          className="w-10 h-10 rounded-lg hover:bg-light-elevated dark:hover:bg-dark-elevated flex items-center justify-center transition-colors cursor-pointer"
          aria-label="Search conversations"
        >
          <Search className="w-5 h-5" />
        </button>
        <CollapseToggle expanded={leftExpanded} onToggle={toggleLeft} side="left" />
      </aside>
    );
  }

  return (
    <aside className="relative h-full surface border-r border-default flex flex-col">
      <div className="p-4 space-y-4">
        <Button
          className="w-full justify-start gap-2"
          variant="primary"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </Button>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search conversations..."
            className={cn(
              "w-full pl-10 pr-4 py-2 rounded-lg",
              "surface elevated border border-default",
              "focus:outline-none focus:ring-2 focus:ring-primary",
              "placeholder:text-muted"
            )}
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        <div className="space-y-1">
          {/* Placeholder for conversation list */}
          <div className="p-3 rounded-lg hover:elevated cursor-pointer transition-colors">
            <div className="flex items-start gap-2">
              <MessageSquare className="w-4 h-4 mt-0.5 text-muted flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">Sample conversation</p>
                <p className="text-xs text-muted truncate">Show me all products...</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <CollapseToggle expanded={leftExpanded} onToggle={toggleLeft} side="left" />
    </aside>
  );
};
