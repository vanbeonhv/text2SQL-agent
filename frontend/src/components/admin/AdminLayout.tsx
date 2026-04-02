import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Topbar } from '../layout/Topbar';
import { cn } from '../../lib/utils';
import { useSidebarStore } from '../../stores/useSidebarStore';
import { useThemeSync } from '../../stores/useThemeStore';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { AdminLeftSidebar } from './AdminLeftSidebar';

export const AdminLayout = () => {
  const { leftExpanded, setLeftExpanded } = useSidebarStore();
  const [isMobile, setIsMobile] = useState(false);

  useThemeSync();
  useKeyboardShortcuts();

  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) setLeftExpanded(false);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [setLeftExpanded]);

  const getGridTemplate = () => {
    if (isMobile) return '1fr';
    const leftWidth = leftExpanded ? '280px' : '60px';
    return `${leftWidth} 1fr`;
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Topbar />
      <div className="flex-1 relative overflow-hidden">
        <div
          className={cn(
            'h-full overflow-hidden',
            isMobile ? 'flex' : 'grid',
            isMobile ? null : 'transition-[grid-template-columns] duration-300 ease-in-out'
          )}
          style={{
            gridTemplateColumns: isMobile ? undefined : getGridTemplate(),
          }}
        >
          {isMobile ? null : <AdminLeftSidebar />}

          <main className="h-full min-h-0 flex flex-col overflow-hidden bg-light-bg dark:bg-dark-bg">
            <div className="flex-1 min-h-0 overflow-y-auto">
              <Outlet />
            </div>
          </main>
        </div>

        {isMobile && leftExpanded && (
          <>
            <button
              type="button"
              className="fixed inset-0 bg-black/50 z-40"
              onClick={() => setLeftExpanded(false)}
              aria-label="Close sidebar"
              onKeyDown={(e) => {
                if (e.key === 'Escape' || e.key === 'Enter') setLeftExpanded(false);
              }}
            />
            <div className="fixed inset-y-0 left-0 w-80 max-w-[85vw] z-50 animate-slide-in-left">
              <AdminLeftSidebar />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

