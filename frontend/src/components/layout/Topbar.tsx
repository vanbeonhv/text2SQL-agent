import { Database, Menu, Activity } from 'lucide-react';
import { Avatar } from '../ui/Avatar';
import { ThemeToggle } from '../ui/ThemeToggle';
import { IconButton } from '../ui/IconButton';
import { useSidebarStore } from '../../stores/useSidebarStore';
import { useState, useEffect } from 'react';

export const Topbar = () => {
  const { setLeftExpanded, setRightExpanded } = useSidebarStore();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <header className="h-16 border-b border-default surface flex items-center justify-between px-4 md:px-6 z-50">
      <div className="flex items-center gap-3">
        {isMobile && (
          <IconButton
            onClick={() => setLeftExpanded(true)}
            aria-label="Open chat history"
            size="md"
          >
            <Menu className="w-5 h-5" />
          </IconButton>
        )}
        <Database className="w-6 h-6 md:w-8 md:h-8 text-primary" />
        <h1 className="text-base md:text-xl font-heading font-semibold truncate">
          Text2SQL Agent
        </h1>
      </div>
      
      <div className="flex items-center gap-2 md:gap-4">
        {isMobile && (
          <IconButton
            onClick={() => setRightExpanded(true)}
            aria-label="Open process visualizer"
            size="md"
          >
            <Activity className="w-5 h-5" />
          </IconButton>
        )}
        <ThemeToggle />
        <Avatar fallback="U" size="md" />
      </div>
    </header>
  );
};
