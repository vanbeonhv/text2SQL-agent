import { Moon, Sun, Monitor } from 'lucide-react';
import { useThemeStore } from '../../stores/useThemeStore';
import { IconButton } from './IconButton';
import { cn } from '../../lib/utils';
import { useState, useRef, useEffect } from 'react';

export const ThemeToggle = () => {
  const { mode, setMode } = useThemeStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const Icon = mode === 'dark' ? Moon : mode === 'light' ? Sun : Monitor;

  return (
    <div className="relative" ref={dropdownRef}>
      <IconButton
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle theme"
        title="Toggle theme"
      >
        <Icon className="w-5 h-5" />
      </IconButton>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 surface elevated rounded-lg shadow-lg border border-default py-1 z-50">
          <button
            onClick={() => {
              setMode('light');
              setIsOpen(false);
            }}
            className={cn(
              'w-full px-4 py-2 text-left flex items-center gap-3 transition-colors',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              mode === 'light' && 'text-primary font-medium'
            )}
          >
            <Sun className="w-4 h-4" />
            Light
          </button>
          <button
            onClick={() => {
              setMode('dark');
              setIsOpen(false);
            }}
            className={cn(
              'w-full px-4 py-2 text-left flex items-center gap-3 transition-colors',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              mode === 'dark' && 'text-primary font-medium'
            )}
          >
            <Moon className="w-4 h-4" />
            Dark
          </button>
          <button
            onClick={() => {
              setMode('system');
              setIsOpen(false);
            }}
            className={cn(
              'w-full px-4 py-2 text-left flex items-center gap-3 transition-colors',
              'hover:bg-light-elevated dark:hover:bg-dark-elevated',
              mode === 'system' && 'text-primary font-medium'
            )}
          >
            <Monitor className="w-4 h-4" />
            System
          </button>
        </div>
      )}
    </div>
  );
};
