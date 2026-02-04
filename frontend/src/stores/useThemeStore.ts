import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { useEffect } from 'react';

type ThemeMode = 'light' | 'dark' | 'system';
type ResolvedTheme = 'light' | 'dark';

interface ThemeStore {
  mode: ThemeMode;
  resolvedMode: ResolvedTheme;
  
  setMode: (mode: ThemeMode) => void;
  setResolvedMode: (mode: ResolvedTheme) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      mode: 'system',
      resolvedMode: 'dark',
      
      setMode: (mode) => set({ mode }),
      setResolvedMode: (mode) => set({ resolvedMode: mode }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

// Hook to sync theme with system preference
export const useThemeSync = () => {
  const { mode, setResolvedMode } = useThemeStore();
  
  useEffect(() => {
    const updateTheme = () => {
      if (mode === 'system') {
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light';
        setResolvedMode(systemTheme);
      } else {
        setResolvedMode(mode as ResolvedTheme);
      }
    };
    
    updateTheme();
    
    if (mode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const listener = (e: MediaQueryListEvent) => {
        setResolvedMode(e.matches ? 'dark' : 'light');
      };
      
      mediaQuery.addEventListener('change', listener);
      return () => mediaQuery.removeEventListener('change', listener);
    }
  }, [mode, setResolvedMode]);
  
  // Apply theme to document
  const { resolvedMode } = useThemeStore();
  
  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolvedMode === 'dark');
  }, [resolvedMode]);
};
