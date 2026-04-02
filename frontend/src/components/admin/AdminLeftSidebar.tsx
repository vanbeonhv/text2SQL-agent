import { NavLink } from 'react-router-dom';
import { Database, Table2 } from 'lucide-react';
import { useSidebarStore } from '../../stores/useSidebarStore';
import { CollapseToggle } from '../ui/CollapseToggle';
import { cn } from '../../lib/utils';

export const AdminLeftSidebar = () => {
  const { leftExpanded, toggleLeft } = useSidebarStore();

  if (!leftExpanded) {
    return (
      <aside className="relative h-full surface border-r border-default flex flex-col items-center py-4 gap-4">
        <div className="w-10 h-10 rounded-lg flex items-center justify-center">
          <Database className="w-5 h-5 text-muted" />
        </div>
        <NavLink
          to="/admin/schema-tables"
          aria-label="Schema & Tables"
          className={({ isActive }) =>
            cn(
              'w-10 h-10 rounded-lg flex items-center justify-center transition-colors cursor-pointer',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              isActive && 'bg-light-elevated dark:bg-dark-elevated text-primary'
            )
          }
        >
          <Table2 className="w-5 h-5" />
        </NavLink>
        <CollapseToggle expanded={leftExpanded} onToggle={toggleLeft} side="left" />
      </aside>
    );
  }

  return (
    <aside className="relative h-full surface border-r border-default flex flex-col overflow-hidden">
      <div className="p-4 border-b border-default">
        <h2 className="text-lg font-heading font-semibold flex items-center gap-2">
          <Database className="w-5 h-5" />
          Admin
        </h2>
        <p className="text-xs text-muted mt-1">Manage schema registry</p>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-2">
        <NavLink
          to="/admin/schema-tables"
          className={({ isActive }) =>
            cn(
              'w-full px-3 py-2 rounded-lg flex items-center gap-2 transition-colors',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              isActive && 'bg-light-elevated dark:bg-dark-elevated text-primary font-medium'
            )
          }
        >
          <Table2 className="w-4 h-4" />
          <span className="text-sm">Schema &amp; Tables</span>
        </NavLink>
      </div>

      <div className="shrink-0 border-t border-default">
        <CollapseToggle expanded={leftExpanded} onToggle={toggleLeft} side="left" />
      </div>
    </aside>
  );
};

