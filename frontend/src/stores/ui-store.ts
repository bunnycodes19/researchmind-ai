import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  explainMode: "simple" | "intermediate" | "expert";
  selectedPaperIds: string[];
  toggleSidebar: () => void;
  setExplainMode: (mode: "simple" | "intermediate" | "expert") => void;
  setSelectedPapers: (ids: string[]) => void;
  togglePaperSelection: (id: string) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  sidebarOpen: true,
  explainMode: "expert",
  selectedPaperIds: [],
  toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),
  setExplainMode: (mode) => set({ explainMode: mode }),
  setSelectedPapers: (ids) => set({ selectedPaperIds: ids }),
  togglePaperSelection: (id) => {
    const current = get().selectedPaperIds;
    if (current.includes(id)) {
      set({ selectedPaperIds: current.filter((x) => x !== id) });
    } else {
      set({ selectedPaperIds: [...current, id] });
    }
  },
}));
