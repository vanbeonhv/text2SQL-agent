import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarStore {
  leftExpanded: boolean;
  rightExpanded: boolean;
  
  toggleLeft: () => void;
  toggleRight: () => void;
  setLeftExpanded: (expanded: boolean) => void;
  setRightExpanded: (expanded: boolean) => void;
}

export const useSidebarStore = create<SidebarStore>()(
  persist(
    (set) => ({
      leftExpanded: true,
      rightExpanded: true,
      
      toggleLeft: () => set((state) => ({ leftExpanded: !state.leftExpanded })),
      toggleRight: () => set((state) => ({ rightExpanded: !state.rightExpanded })),
      setLeftExpanded: (expanded) => set({ leftExpanded: expanded }),
      setRightExpanded: (expanded) => set({ rightExpanded: expanded }),
    }),
    {
      name: 'sidebar-storage',
    }
  )
);
