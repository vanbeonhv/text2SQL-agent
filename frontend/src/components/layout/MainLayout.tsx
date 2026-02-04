import { Topbar } from './Topbar';
import { LeftSidebar } from './LeftSidebar';
import { RightSidebar } from './RightSidebar';
import { ChatArea } from './ChatArea';
import { useSidebarStore } from '../../stores/useSidebarStore';
import { useThemeSync } from '../../stores/useThemeStore';
import { useKeyboardShortcuts } from '../../hooks/useKeyboardShortcuts';
import { cn } from '../../lib/utils';
import { useEffect, useState } from 'react';

export const MainLayout = () => {
  const { leftExpanded, rightExpanded, setLeftExpanded, setRightExpanded } = useSidebarStore();
  const [isMobile, setIsMobile] = useState(false);
  
  // Sync theme with system preference
  useThemeSync();
  
  // Enable keyboard shortcuts
  useKeyboardShortcuts();

  // Handle responsive breakpoints
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      
      // On mobile, collapse sidebars by default
      if (mobile) {
        setLeftExpanded(false);
        setRightExpanded(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, [setLeftExpanded, setRightExpanded]);

  // Calculate grid template columns based on sidebar states
  const getGridTemplate = () => {
    if (isMobile) {
      return '1fr'; // Single column on mobile
    }
    const leftWidth = leftExpanded ? '280px' : '60px';
    const rightWidth = rightExpanded ? '320px' : '60px';
    return `${leftWidth} 1fr ${rightWidth}`;
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Topbar />
      <div className="flex-1 relative overflow-hidden">
        <div
          className={cn(
            'h-full overflow-hidden',
            isMobile ? 'flex' : 'grid',
            !isMobile && 'transition-[grid-template-columns] duration-300 ease-in-out'
          )}
          style={{
            gridTemplateColumns: !isMobile ? getGridTemplate() : undefined,
          }}
        >
          {!isMobile && <LeftSidebar />}
          <ChatArea />
          {!isMobile && <RightSidebar />}
        </div>

        {/* Mobile overlays */}
        {isMobile && (
          <>
            {/* Left sidebar overlay */}
            {leftExpanded && (
              <>
                <div
                  className="fixed inset-0 bg-black/50 z-40"
                  onClick={() => setLeftExpanded(false)}
                  role="button"
                  tabIndex={0}
                  aria-label="Close sidebar"
                  onKeyDown={(e) => {
                    if (e.key === 'Escape' || e.key === 'Enter') {
                      setLeftExpanded(false);
                    }
                  }}
                />
                <div className="fixed inset-y-0 left-0 w-80 max-w-[85vw] z-50 animate-slide-in-left">
                  <LeftSidebar />
                </div>
              </>
            )}

            {/* Right sidebar overlay */}
            {rightExpanded && (
              <>
                <div
                  className="fixed inset-0 bg-black/50 z-40"
                  onClick={() => setRightExpanded(false)}
                  role="button"
                  tabIndex={0}
                  aria-label="Close sidebar"
                  onKeyDown={(e) => {
                    if (e.key === 'Escape' || e.key === 'Enter') {
                      setRightExpanded(false);
                    }
                  }}
                />
                <div className="fixed inset-y-0 right-0 w-80 max-w-[85vw] z-50 animate-slide-in-right">
                  <RightSidebar />
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};
