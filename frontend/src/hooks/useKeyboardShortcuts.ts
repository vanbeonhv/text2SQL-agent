import { useEffect } from 'react';
import { useSidebarStore } from '../stores/useSidebarStore';
import { useChatStore } from '../stores/useChatStore';

export const useKeyboardShortcuts = () => {
  const { toggleLeft, toggleRight } = useSidebarStore();
  const { clearMessages } = useChatStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K - New chat (clear messages)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        clearMessages();
      }

      // Cmd/Ctrl + [ - Toggle left sidebar
      if ((e.metaKey || e.ctrlKey) && e.key === '[') {
        e.preventDefault();
        toggleLeft();
      }

      // Cmd/Ctrl + ] - Toggle right sidebar
      if ((e.metaKey || e.ctrlKey) && e.key === ']') {
        e.preventDefault();
        toggleRight();
      }

      // Escape - Close any open overlays (handled by components)
      if (e.key === 'Escape') {
        // Components will handle their own escape behavior
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleLeft, toggleRight, clearMessages]);
};
